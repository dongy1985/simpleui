(function () {

    // 加载事件
    window.addEventListener('load', function (e) {
        // 単一金額のフォーマット eg:9000→9,000
        function formatter(num) {
              reg = /(?=(\B)(\d{3})+$)/g;
              var temp = num.replace(',','')
              var ss = temp.replace(reg,',')
              return ss
        }
        // 単一金額フォーマットの取消 eg:9,000→9000
        function unFormatter(num) {
              var uu = num.replace(',','')
              return uu
        }
        // 項目明細の一覧明細
        var changeList = $("tr[id^='expensereturndetail_set-']");
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 単一金額テキストボックスのidを取得
                var start="id_expensereturndetail_set-";
                var end="-price";
                var expense_id = start + i + end;
                // 単一金額テキストボックスにフォーカス時、金額フォーマットの取消 eg:9,000→9000
                $("#"+expense_id).focus(function() {
                    var unValue=$(this).val();
                    var uu = unFormatter(unValue);
                    $(this).val(uu);
                  });
                // 単一金額テキストボックスにフォーカスアウト時、金額のフォーマット eg:9000→9,000
                $("#"+expense_id).blur(function() {
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
        // 「項目明細の追加」ボタン押下後のイベント
        $("a").click(function(){
            // 単一金額テキストボックスのidを取得
            var start="id_expensereturndetail_set-";
            var end="-price";
            var expense_nextId = start + next + end;
            // 単一金額テキストボックスにフォーカス時、金額フォーマットの取消 eg:9,000→9000
            $("#"+expense_nextId).focus(function() {
                var unValue=$(this).val();
                var uu = unFormatter(unValue);
                $(this).val(uu);
              });
            // 単一金額テキストボックスにフォーカスアウト時、金額のフォーマット eg:9000→9,000
            $("#"+expense_nextId).blur(function() {
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