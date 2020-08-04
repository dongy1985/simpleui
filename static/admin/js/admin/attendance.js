(function () {

    // 加载事件
    window.addEventListener('load', function (e) {

        // 一覧明細
        var changeList = $("tr[class^='row']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 社員名前
                var name = $(changeList[i]).find("th[class='field-name']").text()
                // 報告状態
                var status = $(changeList[i]).find("td[class='field-status']").text()

                // 報告状態が提出済または承認済の場合、編集リンクを削除する
                if (status == '提出済' || status == '承認済'){
                    // リンク削除
                    $(changeList[i]).find("th[class='field-name']").find('a').remove();
                    // もとの表示内容を追加
                    $(changeList[i]).find("th[class='field-name']").html(name);
                }
             }
        }
        // 選択されている明細の報告状態より削除ボタンの活性化制御
        var btnCtrlFunc = function() {

            // ログインユーザがすスーパーユーザかを判断する(文字列　⇒　Boolean)
           var authPermission = eval($("#authPermission").val().toLowerCase());

            // 一覧明細
            var changeList = $("tr[class^='row']");
            // 削除ボタン
            var delBtn = $(".actions button[data-name='delete_selected']");
            // 提出ボタン
            var confirmBtn = $(".actions button[data-name='commit_button']");
            // 承認ボタン
            var enableBtn = $(".actions button[data-name='confirm_button']");
            // 取消ボタン
            var cancelBtn = $(".actions button[data-name='cancel_button']");
            //  導出ボタン
            var exportBtn = $(".actions button[data-name='export']");
            // 削除ボタンを表示する
            if (delBtn) {
                delBtn.show();
            }
            // 提出ボタンを表示する
            if (confirmBtn) {
                confirmBtn.show();
            }
            // 承認ボタンを表示する
            if (enableBtn) {
                enableBtn.show();
            }
            // 取消ボタンを表示する
            if (cancelBtn) {
                cancelBtn.show();
            }
            // 導出ボタンを表示する
            if (exportBtn) {
                exportBtn.show();
            }
            if (changeList) {
                flg = false;
                for (i = 0; i < changeList.length; i++) {
                    // 選択されているかを判断する
                    var selectedFlg = $(changeList[i]).find('tr').context.classList.contains('selected');
                    // 報告状態
                    var duty_sts = $(changeList[i]).find("td[class='field-status']").text()

                    // 報告状態が提出済または承認済の場合、削除ボタンを隠す
                    if (selectedFlg && (duty_sts == '提出済')){
                        // 削除ボタンを隠す
                        if (delBtn) {
                            delBtn.hide();
                        }
                        // 提出ボタンを隠す
                        if (confirmBtn) {
                            confirmBtn.hide();
                        }
                        // 導出ボタンを隠す
                        if (exportBtn) {
                            exportBtn.hide();
                        }
                    }
                    if (selectedFlg && (duty_sts == '承認済')) {
                        // 提出ボタンを隠す
                        if (confirmBtn) {
                            confirmBtn.hide();
                        }
                        // 削除ボタンを隠す
                        if (delBtn) {
                            delBtn.hide();
                        }
                        // 承認ボタンを隠す
                        if (enableBtn) {
                            enableBtn.hide();
                        }
                    }
                    if (selectedFlg && (duty_sts == '未提出')) {
                        // 承認ボタンを隠す
                        if (enableBtn) {
                            enableBtn.hide();
                        }
                        // 取消ボタンを隠す
                        if (cancelBtn) {
                            cancelBtn.hide();
                        }
                        // 導出ボタンを隠す
                        if (exportBtn) {
                            exportBtn.hide();
                        }
                    }
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