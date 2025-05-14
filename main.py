from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Base
from auth import register_routes

app = Flask(__name__)
app.secret_key = '51275a136660d5b822051b9d4180bf51848855b61b6e79a2262c89d1998dc459'


#SQLite setup
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()


with app.app_context():
      register_routes(app, db_session)

if __name__ == '__main__':
    app.run(debug=True)
 

