import gnupg
import os
from . import constants
from flask import render_template, request, Flask, Response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from .models import db, Audit, Secrets, Users, UsersSecrets

app = Flask(__name__)
db.init_app(app)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
migrate = Migrate(app, db)
gpg = gnupg.GPG()
with open(os.getenv("PGP_PRIVATE_KEY"), "r") as key_file:
    gpg.import_keys(key_data=key_file.read())


class Home(Resource):
    def get(self):
        return Response(render_template('public/home.html'), mimetype='text/html')


class Secret(Resource):
    def get(self):
        from .pgp import encrypt, decrypt
        ec = encrypt(gpg, "test".encode("utf-8"), "", "https://keys.openpgp.org/")
        print(decrypt(gpg, ec.data))

        args = request.args
        key_id = args.get("key_id", None)
        secrets = []

        if key_id is not None:
            user_secrets = UsersSecrets.query.with_entities(UsersSecrets.secret_id).filter_by(key_id=key_id).all()
            user_secrets = [us[0] for us in user_secrets]
            secrets = Secrets.query.filter(Secrets.id.in_(user_secrets)).all()

        secrets_list = [secret.as_json for secret in secrets]
        user_id = Users.query.filter_by(key_id=key_id).first().id
        audit = Audit(user_id=user_id,
                      action_performed=constants.DECRYPTED_SECRET,
                      inputs={"secrets": secrets_list})
        db.session.add(audit)
        db.session.commit()

        return secrets_list

    def post(self):
        data = request.get_json(force=True)
        key_id = data["key_id"]

        secret = Secrets(data["name"], key_id, data["value"])
        user_id = Users.query.filter_by(key_id=key_id).first().id
        audit = Audit(user_id=user_id,
                      action_performed=constants.ENCRYPTED_SECRET,
                      inputs=data)

        db.session.add(audit)
        db.session.add(secret)
        db.session.commit()

        return {"id": secret.id}

    def put(self, secret_id):
        data = request.get_json(force=True)

        secret = Secrets.query.filter_by(id=secret_id).first()
        secret.name = data["name"]
        secret.encrypted_value = data["value"]

        key_id = UsersSecrets.query.filter_by(secret_id=secret.id).first().key_id
        user_id = Users.query.filter_by(key_id=key_id).first().id
        audit = Audit(user_id=user_id,
                      action_performed=constants.MODIFIED_SECRET,
                      inputs=data)

        db.session.add(audit)
        db.session.add(secret)
        db.session.commit()

        return {"id": secret_id}, 201

    def delete(self, key_id):
        secret = Secrets.query.filter_by(id=key_id).first()
        audit = Audit(user_id="",
                      action_performed=constants.DELETED_SECRET,
                      inputs={})
        db.session.delete(secret)
        db.session.add(audit)
        db.session.commit()
        return {"success": "True"}, 204


api.add_resource(Home, "/home")
api.add_resource(Secret, "/secret", "/secret/<secret_id>")

if __name__ == "__main__":
    app.run(debug=True)
