from flask import Flask, jsonify, request, send_from_directory
# from auth import admin_required
from models import User, Base, Product, Sale, Payment
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import CORS
from mpesa import make_stk_push
from datetime import timedelta
from werkzeug.utils import secure_filename
from generatePdf import generate_pdf
from utilities.decorators import admin_required
from werkzeug.utils import secure_filename
import os
import uuid
from flask import request, jsonify



load_dotenv()


app = Flask(__name__)
from flask_cors import CORS

CORS(
    app,
    origins=["http://127.0.0.1:5500"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
)# Enable CORS for all routes

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# ✅ ADD THEM HERE
@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"error": "Missing token"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Invalid token"}), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has been revoked"}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Fresh token required"}), 401


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("db_url")

if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise ValueError("Database URL not set")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("jwt_secret_key")

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
sessionLocal = sessionmaker(bind=engine)
# db_session = sessionLocal()

def get_db():
    return sessionLocal()

Base.metadata.create_all(engine)    

@app.route("/")
def home():
    return "Welcome to the Flask API!"

@app.route("/register", methods=["POST"])
def register():
    with get_db() as db:
        if request.method != "POST":
             return jsonify({"error": "Method not allowed"}), 405
    
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  

        try:
            new_user = User(full_name=full_name, 
                            email=email, 
                            password=hashed_password,
                            role="Cashier")
            db.add(new_user)
            db.commit()
            
            access_token = create_access_token(identity=email)
            
            if access_token:
                return jsonify({"message": "Registration Successful", "access_token": access_token}), 201
            else:
                return jsonify({"error": ""}), 500

        except Exception as e:
            db.rollback()
            return jsonify({"error": "Error occurred while registering user"}), 500

@app.route("/login", methods=["POST"])
def login():
        with get_db() as db:
            # Process login logic here
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400
            
            user = db.query(User).filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                
                access_token = create_access_token(identity=user.email)

                return jsonify({"message": "Login Successful", "access_token": access_token}), 200
            return jsonify({"error": "Invalid email or password"}), 401

revoked_tokens = set()

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    revoked_tokens.add(jti)

    return jsonify({"message": "Logout successful"}), 200

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():
    with get_db() as db:

        if request.method == "GET":
            products = db.query(Product).all()

            return jsonify([
                {
                    "id": Product.id,
                    "product_name": Product.product_name,
                    "quantity": Product.quantity,
                    "price": Product.price,
                    "total_price": Product.total_price
                }
                for Product in products
            ]), 200

        elif request.method == "POST":
            data = request.get_json(force=True)

            print("data:-----------", request.get_json())

            product_name = data.get("product_name")
            quantity = data.get("quantity")
            price = data.get("price")

            if quantity is None or price is None:
                return jsonify({"error": "Quantity and price are required"}), 400
 
            quantity = int(quantity)
            price = float(price)

            if not product_name or not quantity or not price:
                return jsonify({"error": "Missing required fields"}), 400
            # total_price = float(quantity) * float(price)

            current_user_email = get_jwt_identity()
            user = db.query(User).filter_by(email=current_user_email).first()

            new_product = Product(
                user_id=user.id,
                product_name=product_name,
                quantity=quantity,
                price=price,
                # total_price=total_price
            )

            db.add(new_product)
            db.commit()

            return jsonify({"message": "Product created"}), 201
        
@app.route("/products/<int:id>", methods=["PUT"])
@jwt_required(optional=True)
def update_product(id):
        
    with get_db() as db:
        product = db.query(Product).filter_by(id=id).first()

        if not product:
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json()

        product_name = data.get("product_name")
        quantity = data.get("quantity")
        price = data.get("price")

        if quantity is not None:
            product.quantity = int(quantity)

        if price is not None:
            product.price = float(price)

        if product_name is not None:
            product.product_name = product_name


        db.commit()

        return jsonify({"message": "Product updated successfully"}), 200
    
@app.route("/products/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    if request.method == "OPTIONS":
        return '', 200
    
    with get_db() as db:
        product = db.query(Product).filter_by(id=id).first()

        if not product:
            return jsonify({"error": "Not found"}), 404

        db.delete(product)
        db.commit()

        return jsonify({"message": "Deleted"}), 200
    
@app.route("/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    with get_db() as db:
        if request.method == "POST":
            # Process sales creation logic here
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            product_id = data.get("product_id")

            if not product_id:
                return jsonify({"error": "Product ID is required"}), 400

            existing_product = db.query(Product).filter_by(id=product_id).first()

            if not existing_product:
                return jsonify({"error": "Product not found"}), 404

            new_sale = Sale(product_id=product_id)
            #first create the sale record
            #attach the sale id to the individual items. 
            # then make the stk push request to mpesa. 
            # then update the sale record with the payment details after the callback is received from mpesa in the /stk-call-back route
            try:
                db.add(new_sale)
                db.commit()
                db.refresh(new_sale)
            except Exception as e:
                db.rollback()
                return jsonify({"error": "Error occurred while creating sale"}), 500

            return jsonify({"message": "Sale created successfully", "sale_id": new_sale.id}), 201
        else:
                # Process sales retrieval logic here
                sales = db.query(Sale).all()

                sales_list = [
                    {
                        "id": sale.id,
                        "product_id": sale.product_id,
                        "created_at": sale.created_at
                    }
                    for sale in sales
                ]
                return jsonify(sales_list), 200

@app.route('/stk-push', methods=['POST'])
def stk_push():
    data = request.get_json()
    
    stk_response = make_stk_push(data)
    print("STK Push Response:", stk_response)

#create a payment with id, sale_id, mrid, crid, created_at
    try:
        with get_db() as db:
            new_payment = Payment(
                sale_id=data.get("sale_id"),
                merchant_request_id=stk_response.get("MerchantRequestID"),
                checkout_request_id=stk_response.get("CheckoutRequestID"),
                status="Pending"
            )

            db.add(new_payment)
            db.commit()

    except Exception as e:
        print("Error saving payment:", str(e))

    return jsonify(stk_response)

@app.route('/stk-call-back', methods=['POST'])
def call_back():

    data = request.get_json()

    try:
        stk_callback = data["Body"]["stkCallback"]

        merchant_request_id = stk_callback.get("MerchantRequestID")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")

        with get_db() as db:
            #fetch the payment record using mrid and crid
            payment = db.query(Payment).filter_by(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id).first()
            
            if not payment:
                return jsonify({"error": "Payment not found"}), 404
            
            # update based on success or failure
            if result_code == 0:
                callback_items = stk_callback["CallbackMetadata"]["Item"]

                metadata = {item["Name"]: item.get("Value") for item in callback_items}
                print("Payment Metadata:", metadata)

                payment.transaction_code = metadata.get("MpesaReceiptNumber")
                payment.amount = metadata.get("Amount")
                payment.phone_paid = metadata.get("PhoneNumber")
                payment.status = "Success"
                
                #Now generate a pdf receipt using the metadata and save it to the reciepts folder with the name as the transaction code
                # receipt_text = f"""Payment Receipt ..."""
                # generate_pdf(receipt_text, f"{payment.transaction_code}.pdf")
                receipt_text = f"""Payment Receipt
                        Transaction Code: {payment.transaction_code}
                        Amount: {payment.amount}
                        Phone Number: {payment.phone_paid}
                        Status: {payment.status}
                        Thank you for your payment!"""
                generate_pdf(receipt_text, f"{payment.transaction_code}.pdf")

            else:
                payment.status = "Failed"
                print("Payment Failed:", payment.status)

            db.commit()
        return jsonify({"message": "Callback processed successifully"}), 200
    except Exception as e:
        print("Callback error:", str(e))
        return jsonify({"error": "Failed to process callback"}), 500
    # return jsonify({"message": "Callback received"}), 200
    
#add a route for mpesa-payments its a get request it should fetch payments from payments table in db
@app.route("/mpesa-payments", methods=["GET"])
@jwt_required()
def get_mpesa_payments():
    with get_db() as db:
        payments = db.query(Payment).all()

        payments_list = [
            {
                "id": payment.id,
                "sale_id": payment.sale_id,
                "merchant_request_id": payment.merchant_request_id,
                "checkout_request_id": payment.checkout_request_id,
                "transaction_code": payment.transaction_code,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at
            }
            for payment in payments
        ]

        return jsonify(payments_list), 200
    
@app.route("/admin/users", methods=["GET"])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "role": u.role
        } for u in users
    ])


@app.route("/admin/users/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(id):
    with get_db() as db:
        user = User.query.get(id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        db.delete(user)
        db.commit()

    return jsonify({"msg": "User deleted"})




#

if __name__ == "__main__":
    app.run()