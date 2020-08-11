(function () {

    // 加载事件
    window.addEventListener('load', function (e) {
        // 保存ボタン
        var saveBtn = $(".el-button--primary");

        // 一覧明細
        var changeList = $("tr[id^='expensereturndetail_set-']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                var start="id_expensereturndetail_set-";
                var end="-price";
                var expense_id = start + i + end;

                function formatter(num) {
                      reg = /(?=(\B)(\d{3})+$)/g;
                      var temp = num.replace(',','')
                      var ss = temp.replace(reg,',')
                      return ss
                }
                function unFormatter(num) {
                      var uu = num.replace(',','')
                      return uu
                }

                  // テキストボックスにフォーカス時、フォームの背景色を変化
                $("#"+expense_id).focus(function() {
                    var unValue=$(this).val();
                    var uu = unFormatter(unValue);
                    $(this).val(uu);
                    $(this).css('background-color', 'pink');
                  });
                $("#"+expense_id).blur(function() {
                    var curValue=$(this).val();
                    var amtreg=/^([1-9]\d{0,9}|0)([.]?|(\.\d{1,2})?)$/;
                    if(!amtreg.test(curValue)){
                        swal("OMG!", "正しい金額を入力してください！", "error");
                        saveBtn.hide();
                        return;
                    }
                    var ss = formatter(curValue);
                    saveBtn.show();
                    $(this).val(ss);
                    $(this).css('background-color', '#ffc');
                  });

             }
        }

        var next = changeList.length-1;
        // 明細一覧のチェックボックスのイベント
        $("a").click(function(){
            var start="id_expensereturndetail_set-";
            var end="-price";
            var expense_nextId = start + next + end;

            function formatter(num) {
                  reg = /(?=(\B)(\d{3})+$)/g;
                  var temp = num.replace(',','')
                  var ss = temp.replace(reg,',')
                  return ss
            }
            function unFormatter(num) {
                  var uu = num.replace(',','')
                  return uu
            }
              // テキストボックスにフォーカス時、フォームの背景色を変化
            $("#"+expense_nextId).focus(function() {
                var unValue=$(this).val();
                var uu = unFormatter(unValue);
                $(this).val(uu);
                $(this).css('background-color', 'pink');
              });

            $("#"+expense_nextId).blur(function() {
                var curValue=$(this).val();
                var amtreg=/^([1-9]\d{0,9}|0)([.]?|(\.\d{1,2})?)$/;
                if(!amtreg.test(curValue)){
                    swal("OMG!", "正しい金額を入力してください！", "error");
                    saveBtn.hide();
                    return;
                }
                var ss = formatter(curValue);
                saveBtn.show();
                $(this).val(ss);
                $(this).css('background-color', '#ffc');
              });
            next = next + 1;
        });

    });
})();