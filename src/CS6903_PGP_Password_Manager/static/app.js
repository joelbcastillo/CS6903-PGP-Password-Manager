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
        let password = $('#private-key-password').val();
        console.log(password);
        privateKey = await privateKeyFile;
        PgpKey.load(privateKey, password, key => {
            keyManager = key;
        });
        if (keyManager) {
            $('#load-key-status-area').show();
            $('#l1oad-key-status-area').removeClass().addClass('alert alert-success');
            $('#load-key-status').html("<span>Successfully loaded key.</span>");
            $('#load-key').click(loadKey);
            $('#get-secrets').prop('disabled', false);
        } else {
            $('#load-key-status-area').show();
            $('#load-key-status-area').removeClass().addClass('alert alert-danger');
            $('#load-key-status').html("<span>Failed to load key. Please make sure you provided a password (if needed).</span>");
            $('#load-key').click(loadKey);
        }
    }

    function getSecrets() {
        keyId = keyManager.id();
        $.get({
            url: "/secret",
            data: {
                "key_id": keyId,
            },
            success: function (data) {
                console.log(data['secrets']);
                keyManager.decrypt(data['secrets'], secrets => {
                    console.log(typeof(secrets))
                    jsonSecrets = JSON.parse(secrets);
                    $.each(jsonSecrets, function (i, item) {
                        console.log(item);
                    })
                }
                );
            }
        });
    }

    $('#load-key').click(loadKey);
    $('#get-secrets').click(getSecrets);
});
