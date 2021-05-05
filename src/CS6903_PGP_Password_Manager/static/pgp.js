class PgpKey {
    constructor(key) {
        this._key = key;
        if (this.canDecrypt()) {
            this._ring = new kbpgp.keyring.KeyRing();
            this._ring.add_key_manager(key);
        }
    }

    public() {
        return this._key.armored_pgp_public;
    }

    id() {
        return this._key.get_pgp_short_key_id();
    }

    nickname() {
        return this._key.userids[0].get_username();
    }

    encrypt(text, onDone) {
        kbpgp.box({ msg: text, encrypt_for: this._key }, (_, cipher) =>
            onDone(cipher));
    }

    canDecrypt() {
        return this._key.can_decrypt();
    }

    decrypt(cipher, onDone) {
        kbpgp.unbox({ keyfetch: this._ring, armored: cipher, progress_hook: null }, (_, literals) =>
            onDone(literals[0].toString()));
    }

    static generate(nickname, onDone) {
        let opt = { userid: nickname, primary: { nbits: 1024 }, subkeys: [] };
        kbpgp.KeyManager.generate(opt, (_, key) =>
            key.sign({}, () =>
                key.export_pgp_public({}, () =>
                    onDone(new PgpKey(key)))));
    }

    static load(publicKey, password, onDone) {
        kbpgp.KeyManager.import_from_armored_pgp({ armored: publicKey }, function (err, key) {
            if (!err) {
                if (key.is_pgp_locked()) {
                    key.unlock_pgp({
                        passphrase: password
                    }, function (err) {
                        if (!err) {
                            onDone(new PgpKey(key));
                        } else {
                            onDone(null);
                        }
                    })
                } else {
                    onDone(new PgpKey(key));
                }
            }
        });
    }
}
