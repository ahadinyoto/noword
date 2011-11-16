/*
 
 Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto

 Licensed under GNU General Public License version 2.0 and above
 
*/

// Depends on JQuery

var noword = { 
    decryptList: {},

    _decrypt: function (key, ciphertext, debug) {
        cipher = cryptoHelpers.base64.decode(ciphertext);
        
        if (debug) 
            console.log("Data: " + cipher);
        
        iv = cipher.slice(0, 16);
        cipher = cipher.slice(16);

        if (debug)
            console.log("CT: " + cipher + ", Length: " + cipher.length);

        keyhex = cryptoHelpers.convertStringToByteArray(key);
        hextext = slowAES.decrypt(cipher, slowAES.modeOfOperation.CBC, keyhex, iv);

        if (debug)
            console.log("PT: " + hextext + ", Length: " + hextext.length);

        plaintext = cryptoHelpers.convertByteArrayToString(hextext);
        if (debug)
            console.log("Length: " + plaintext.length);
            console.log(plaintext);

        return plaintext;
    },

    _padKey: function (key) {
        var padsize = 16 - (key.length % 16);
        var padded_key = key;
        for (var i = 0; i < padsize; i++) {
            padded_key += "."
        }
        return padded_key;
    },

    decrypt: function (id) {
        var node_text       = $("#" + id + "-text");
        var node_key        = $("#" + id + "-key");
        var node_key_text   = $("#" + id + "-key-text");
        var node_error      = $("#" + id + "-error");

        node_error.css("display", "none");
        node_error.text("Wrong password. Please try again.");

        if (Modernizr.localstorage && localStorage["noword-"+id]) {
            key = localStorage["noword-"+id];
        }
        else {
            key = node_key_text.val();
        }

        var cipherText = node_text.text();
        var paddedKey = noword._padKey(key)
        var plainText = noword._decrypt(paddedKey, cipherText, false);

        checkString = "{{" + id + "}}";
        if (plainText.indexOf(checkString) == 0) {
            plainText = plainText.replace(checkString, "");

            plainText = $.trim(plainText);

            node_text.text("\n" + plainText + "\n\n");
            node_key.slideUp('fast');
            node_text.delay(300).slideDown(500);
            noword.decryptList[id] = true;
            // may collide for long usage
            if (Modernizr.localstorage)
                localStorage["noword-"+id] = key;
        } 
        else {
            node_error.fadeIn(1000);
        }

    },

    handleDisclose: function (id, isEncrypted) {
        // relies on JQuery $()

        // get key
        // then show the plaintext
        var node_text = $("#" + id + "-text");

        if (isEncrypted) {
            if (Modernizr.localstorage && localStorage["noword-"+id]) {
                if (! (id in noword.decryptList)) {
                    noword.decrypt(id); 
                }
            }
            else if (! (id in noword.decryptList)) {
                node_key = $("#" + id + "-key");
                node_key.slideToggle('fast');
            }
        }
        else {
            node_text.slideToggle("fast");
        }
    }
}
