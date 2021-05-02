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
    let privateKeyUploadElement = document.getElementById('private-key');
    let privateKeyFile = readKey(privateKeyUploadElement.files[0]);
    privateKey = await privateKeyFile;
    keyManager = PgpKey(privateKey);
}

document.getElementById('load-key').addEventListener('click', loadKey);
