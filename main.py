import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cafes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

    with app.app_context():
        db.create_all()




@app.route("/")
def home():
    with app.app_context():
        cafes = db.session.query(Cafe).all()

    return render_template("all-cafes.html", cafes=cafes, coffee_price=4.5)



@app.route("/all")
def get_all_cafes():
    with app.app_context():
        cafes = db.session.query(Cafe).all()
    return render_template("all-cafes.html", cafes=cafes, coffee_price=4.5)


@app.route("/search")
def search():
    value_change = {
        "on": "1",
        "none": "0",
        "":"0"
    }

    location_dict = {
        "Select Area": "All",
        "1": "All",
        "2": "Bankside",
        "3": "Barbican",
        "4": "Bermondsey",
        "5": "Borough",
        "6": "Clerkenwell",
        "7": "Hackney",
        "8": "London Bridge",
        "9": "Peckham",
        "10": "Shoreditch",
        "11": "South Kensington",
        "12": "Whitechapel"
    }

    filter_dict = {
        "wc": "",
        "wifi": "",
        "sockets": "",
        "calls": ""
    }


    for item in filter_dict:
        if request.args.get(item):
            filter_dict[item] = value_change[request.args.get(item)]

    if request.args.get("location"):
        location = location_dict[request.args.get("location")]

    criteria = {}
    if filter_dict["wc"] != "":
        criteria["has_toilet"] = 1
    if filter_dict["wifi"] != "":
        criteria["has_wifi"] = 1
    if filter_dict["sockets"] != "":
        criteria["has_sockets"] = 1
    if filter_dict["calls"] != "":
        criteria["can_take_calls"] = 1
    if location != "All":
        criteria["location"] = location

    cafes = db.session.query(Cafe).filter_by(**criteria).all()

    price = float(request.args.get("price"))
    cafes1 = [ cafe for cafe in cafes if not float(cafe.coffee_price.replace("£", "")) >= price]


    if cafes:
        return render_template("all-cafes.html", cafes=cafes1, coffee_price = price)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})



if __name__ == '__main__':
    app.run(debug=True)
