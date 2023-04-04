var infor_btn = document.getElementById('info_btn1');
// console.log(infor_btn);
var input_lexical = document.getElementById('input_lexical');
// console.log(input_lexical);
var input_grammar = document.getElementById('input_grammar');
// console.log(input_grammar);
var input_code = document.getElementById('input_code');
// console.log(input_code);
infor_btn.addEventListener('click', function () {
    // var file = input.files[0];
    var file1 = input_lexical.files.item(0);
    if (file1) {
        result1.innerHTML =
            'Name:' + file1.name + '\nType:' + file1.type + '\nSize:' + file1.size + 'B';
    } else {
        result1.innerHTML = 'No Lexical File Selected';
    };
    var reader1 = new FileReader();
    reader1.readAsText(file1, 'UTF-8');
    reader1.onload = function () {
        r_result1 = this.result;
        document.getElementById("content1").innerHTML += r_result1.replace(/[<>&"\n]/g, function (c) {
            return { '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', '\n': '<br/>' }[c];
        })
    }
    var file2 = input_code.files.item(0);
    if (file2) {
        result2.innerHTML =
            '\n\nName:' + file2.name + '\nType:' + file2.type + '\nSize:' + file2.size + 'B';
    } else {
        result2.innerHTML = '\nNo Code File Selected';
    }
    var reader2 = new FileReader();
    reader2.readAsText(file2, 'UTF-8');
    reader2.onload = function () {
        r_result2 = this.result;
        document.getElementById("content2").innerHTML += r_result2.replace(/[<>&"\n]/g, function (c) {
            return { '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', '\n': '<br/>' }[c];
        })
    }
    var file3 = input_grammar.files.item(0);
    if (file3) {
        result3.innerHTML =
            '\n\nName:' + file3.name + '\nType:' + file3.type + '\nSize:' + file3.size + 'B';
    } else {
        result3.innerHTML = '\nNo Grammar File Selected';
    }
    var reader3 = new FileReader();
    reader3.readAsText(file3, 'UTF-8');
    reader3.onload = function () {
        r_result3 = this.result;
        document.getElementById("content3").innerHTML += r_result3.replace(/[<>&"\n]/g, function (c) {
            return { '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', '\n': '<br/>' }[c];
        })
    }
});

// submit_btn.addEventListener('click', function () {
//     var file1 = input_grammar.files.item(0);
//     var reader1 = new FileReader();
//     reader1.readAsText(file1, 'UTF-8');
//     reader1.onload = function () {
//         r_result1 = this.result;
//         var formData = new FormData();
//         formData.append('lexical', r_result1);

//         fetch('./upload_file', {
//             method: 'PUT',
//             body: formData
//         })
//     }
// })