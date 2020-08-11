(function () {

    // 加载事件
    window.addEventListener('load', function (e) {
       // 金額のフォーマット eg:9000→9,000
       function formatter(num) {
              reg = /(?=(\B)(\d{3})+$)/g;
              var temp = num.replace(',','')
              var ss = temp.replace(reg,',')
              return ss
        }
        // 金額フォーマットの取消 eg:9,000→9000
        function unFormatter(num) {
              var uu = num.replace(',','')
              return uu
        }
        // 通勤手当の一覧明細
        var changeList = $("tr[id^='dutydetail_set-']");
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 金額テキストボックスのidを取得
                var start="id_dutydetail_set-";
                var end="-trafficAmount";
                var duty_id = start + i + end;
                // 金額テキストボックスにフォーカス時、金額フォーマットの取消 eg:9,000→9000
                $("#"+duty_id).focus(function() {
                    var unValue=$(this).val();
                    var uu = unFormatter(unValue);
                    $(this).val(uu);
                  });
                // 金額テキストボックスにフォーカスアウト時、金額のフォーマット eg:9000→9,000
                $("#"+duty_id).blur(function() {
                    var curValue=$(this).val();
                    var amtreg=/^([1-9]\d{0,9}|0)([.]?|(\.\d{1,2})?)$/;
                    if(!amtreg.test(curValue)){
                        swal("OMG!", "正しい金額を入力してください！", "error");
                        return;
                    }
                    var ss = formatter(curValue);
                    $(this).val(ss);
                  });

             }
        }

        var next = changeList.length-1;
        // 「通勤手当明細の追加」ボタン押下後のイベント
        $("a").click(function(){
            // 金額テキストボックスのidを取得
            var start="id_dutydetail_set-";
            var end="-trafficAmount";
            var duty_nextId = start + next + end;
            // 金額テキストボックスにフォーカス時、金額フォーマットの取消 eg:9,000→9000
            $("#"+duty_nextId).focus(function() {
                var unValue=$(this).val();
                var uu = unFormatter(unValue);
                $(this).val(uu);
              });
            // 金額テキストボックスにフォーカスアウト時、金額のフォーマット eg:9000→9,000
            $("#"+duty_nextId).blur(function() {
                var curValue=$(this).val();
                var amtreg=/^([1-9]\d{0,9}|0)([.]?|(\.\d{1,2})?)$/;
                if(!amtreg.test(curValue)){
                    swal("OMG!", "正しい金額を入力してください！", "error");
                    return;
                }
                var ss = formatter(curValue);
                $(this).val(ss);
              });
            next = next + 1;
        });

    });
})();