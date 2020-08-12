(function () {

    // 加载事件
    window.addEventListener('load', function (e) {

        //郵便番号にハイフンを自動挿入するメソッド
        function insertStr(input){
            return input.slice(0, 3) + '-' + input.slice(3,input.length);
        }

        //入力時に郵便番号に自動でハイフンを付けるイベント
        $("#id_zipCode").on('keyup',function(e){
            var input = $(this).val();

            //削除キーではハイフン追加処理が働かないように制御（8がBackspace、46がDelete)
            var key = event.keyCode || event.charCode;
            if( key == 8 || key == 46 ){
                return false;
            }

            //３桁目に値が入ったら発動
            if(input.length === 3){
                $(this).val(insertStr(input));
            }
          });

        //フォーカスが外れた際、本当に4桁目に'-'がついているかチェック。なければ挿入するイベント
        //これでコピペした場合にも反応できるハズ？
        $("#id_zipCode").on('blur',function(e){
            var input = $(this).val();

            //４桁目が'-(ハイフン)’かどうかをチェックし、違ったら挿入
            if(input.length >= 3 && input.substr(3,1) !== '-'){
                $(this).val(insertStr(input));
            }
        });


        // 電話番号にハイフンを自動挿入するメソッド
        function formatter(phonenum) {
              var snum = phonenum.slice(0, 3)
              var mnum = phonenum.slice(3, 7)
              var fnum = phonenum.slice(7, 11)
              var result = snum + '-' + mnum + '-' + fnum
              return result
        }

        // 電話番号テキストボックスにフォーカスアウト時、電話番号にハイフンを挿入する
        $("#id_phone").blur(function() {
            var curValue=$(this).val();
            //電話番号に'-(ハイフン)’があるかどうかをチェックし、違ったら挿入
            if(curValue.length == 11 && curValue.indexOf('-') == -1){
                var result = formatter(curValue);
                $(this).val(result);
            }

          });

    });
})();
