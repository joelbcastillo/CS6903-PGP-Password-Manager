$(document).ready(function () {
    var privateKey = null;
    var keyManager = null;
    function readKey(file, onLoadCallback) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () {
                resolve(
                    reader.result
                );
            };
            reader.onerror = reject;
            reader.readAsText(file);
        })
    }

    async function loadKey() {
        $('#load-key-status-area').hide();
        let privateKeyFile = readKey($('#private-key')[0].files[0]);
        let password = $('#private-key-password').value;
        privateKey = await privateKeyFile;
        PgpKey.load(privateKey, password, key => {
            keyManager = key;
        });
        if (keyManager) {
            $('#load-key-status-area').show();
            $('#load-key-status-area').removeClass().addClass('alert alert-success');
            $('#load-key-status').html("<span>Successfully loaded key.</span>");
            // $('#load-key').click(loadKey);
        } else {
            $('#load-key-status-area').show();
            $('#load-key-status-area').removeClass().addClass('alert alert-danger');
            $('#load-key-status').html("<span>Failed to load key. Please make sure you provided a password (if needed).</span>");
            $('#load-key').click(loadKey);
        }
    }

    function getSecrets(key) {
        keyId = key.id();
        secrets = [];
        $.ajax({
            url: "/secrets/" + keyId,
            success: function (data) {
                $.each(data, function (ndx, val) {
                    key.decrypt(val, plain => { secrets[ndx] = plain });
                });
            }
        });
    }

    



    $('#load-key').click(loadKey);
});
