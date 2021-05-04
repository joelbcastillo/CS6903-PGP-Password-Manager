import json
import os

import gnupg
from flask import Flask, Response, render_template, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from . import constants
from .models import Audit, Secrets, Users, UsersSecrets, db
from .pgp import decrypt, encrypt

app = Flask(__name__)
db.init_app(app)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
migrate = Migrate(app, db)
key_server = os.getenv("KEY_SERVER", "https://keys.openpgp.org/")
passphrase = os.getenv("PGP_PASSWORD")
gpg = gnupg.GPG()

with open(os.getenv("PGP_PRIVATE_KEY"), "r") as key_file:
    gpg.import_keys(key_data=key_file.read())


class Home(Resource):
    def get(self):
        return Response(render_template("public/home.html"), mimetype="text/html")


class Secret(Resource):
    def get(self):
        args = request.args
        key_id = args.get("key_id", None)
        secrets = []

        if key_id is not None:
            user_secrets = (
                UsersSecrets.query.with_entities(UsersSecrets.secret_id)
                .filter_by(key_id=key_id)
                .all()
            )
            user_secrets = [us[0] for us in user_secrets]
            secrets = Secrets.query.filter(Secrets.id.in_(user_secrets)).all()

        secrets_list = json.dumps([secret.as_json for secret in secrets])
        secrets_list_encrypted = encrypt(gpg, str(secrets_list), key_id, key_server, passphrase)
        user_id = Users.query.filter_by(key_id=key_id).first().id
        audit = Audit(
            user_id=user_id,
            action_performed=constants.DECRYPTED_SECRET,
            inputs={"secrets": secrets_list},
        )
        db.session.add(audit)
        db.session.commit()

        return {"secrets": secrets_list_encrypted.data.decode("utf-8")}

    def post(self):
        value = request.files["file"].read()

        decrypted_data = decrypt(gpg, value, passphrase)
        data_json = json.loads(decrypted_data.data.decode("utf-8"))
        key_id = data_json["key_id"]
        secret = Secrets(name=data_json["name"], encrypted_value=value)
        user_id = Users.query.filter_by(key_id=key_id).first().id
        audit = Audit(
            user_id=user_id,
            action_performed=constants.ENCRYPTED_SECRET,
            inputs={"encrypted_value": str(value)},
        )

        db.session.add(audit)
        db.session.add(secret)
        db.session.commit()

        return {"id": str(secret.id)}

    def put(self, secret_id):
        value = request.files["file"].read()

        decrypted_data = decrypt(gpg, value, passphrase)
        data_json = json.loads(decrypted_data.data.decode("utf-8"))

        secret = Secrets.query.filter_by(id=secret_id).first()
        secret.name = data_json["secret_info"]["name"]
        secret.encrypted_value = data_json["secret_info"]["encrypted_value"]

        user_id = Users.query.filter_by(key_id=data_json["key_id"]).first().id
        audit = Audit(
            user_id=user_id,
            action_performed=constants.MODIFIED_SECRET,
            inputs={"secret_id": secret.id, "encrypted_value": secret.encrypted_value},
        )

        db.session.add(audit)
        db.session.add(secret)
        db.session.commit()

        return {"id": str(secret.id)}, 201


api.add_resource(Home, "/home")
api.add_resource(Secret, "/secret", "/secret/<secret_id>")

if __name__ == "__main__":
    app.run(debug=True)
