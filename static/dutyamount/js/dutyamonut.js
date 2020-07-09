(function () {

    // 加载事件
    window.addEventListener('load', function (e) {

        // 一覧明細
        var changeList = $("tr[class^='row']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 社員名前
                var applyName = $(changeList[i]).find("th[class='field-applyName']").text()
                // 報告状態
                var traffic_status = $(changeList[i]).find("td[class='field-trafficStatus']").text()

                // 報告状態が提出済または承認済の場合、編集リンクを削除する
                if (traffic_status == '提出済' || traffic_status == '承認済'){
                    // リンク削除
                    $(changeList[i]).find("th[class='field-applyName']").find('a').remove();
                    // もとの表示内容を追加
                    $(changeList[i]).find("th[class='field-applyName']").html(applyName);
                }
             }
        }
        // 選択されている明細の報告状態より削除ボタンの活性化制御
        var btnCtrlFunc = function() {

            // ログインユーザがすスーパーユーザかを判断する
           var authPermission = eval($("#authPermission").val().toLowerCase());

            // 一覧明細
            var changeList = $("tr[class^='row']");
            // 削除ボタン
            var delBtn = $(".actions button[data-name='delete_selected']");
            // 取消ボタン
//            var cancelBtn = $(".actions button[data-name='cancel']");
            // 削除ボタンを表示する
            if (delBtn) {
                delBtn.show();
            }

            if (changeList) {
                flg = false;
                for (i = 0; i < changeList.length; i++) {
                    // 選択されているかを判断する
                    var selectedFlg = $(changeList[i]).find('tr').context.classList.contains('selected');
                    // 報告状態
                    var traffic_status = $(changeList[i]).find("td[class='field-trafficStatus']").text()

                    // 報告状態が提出済または承認済の場合、削除ボタンを隠す
                    if (selectedFlg && (traffic_status == '提出済' || traffic_status == '承認済')){
                        // 削除ボタンを隠す
                        if (delBtn) {
                            delBtn.hide();
                        }

                        // 管理者以外の場合、承認済のデータが取消できない
//                        if (authPermission == 'False' && cancelBtn && duty_sts == '承認済') {
//                            cancelBtn.hide();
                        }
                        break;
                    }
                 }
            }

        // 明細一覧のチェックボックスのイベント
        $(".action-checkbox").bind('click', function(e){
            // 削除ボタンまたは取消ボタンの制御
            btnCtrlFunc();
        });

        // 一覧ヘッダ部のチェックボックスのイベント
        $(".action-checkbox-column").bind('click', function(e){
            // 削除ボタンまたは取消ボタンの制御
            btnCtrlFunc();
        });

    });
})();