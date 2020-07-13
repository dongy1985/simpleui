(function () {

    // 加载事件
    window.addEventListener('load', function (e) {

        // 一覧明細
        var changeList = $("tr[class^='row']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 資産番号
                var duty_code = $(changeList[i]).find("th[class='field-asset_code']").text()
                // 資産借出状態
                var lend_sts = $(changeList[i]).find("td[class='field-lend_status']").text()
                // 報告状態が承認済以後の場合、編集リンクを削除する
                if (lend_sts == '承認済' || lend_sts == '貸出済' || lend_sts == '返却済'){
                    // リンク削除
                    $(changeList[i]).find("th[class='field-asset_code']").find('a').remove();
                    // もとの表示内容を追加
                    $(changeList[i]).find("th[class='field-asset_code']").html(duty_code);
                }
             }
        }
        // 選択されている明細の報告状態より削除ボタンの活性化制御
        var btnCtrlFunc = function() {

            // ログインユーザがすスーパーユーザかを判断する
           var authPermission = eval($("#authPermission").val().toLowerCase());

            // 一覧明細
            var changeList = $("tr[class^='row']");

            // 承認ボタン
            var requestBtn = $(".actions button[data-name='apply_request']");
            // 拒否ボタン
            var denyBtn = $(".actions button[data-name='apply_deny']");
            // 貸出ボタン
            var lendBtn = $(".actions button[data-name='apply_lend']");
            // 返済ボタン
            var backBtn = $(".actions button[data-name='apply_back']");

            // 削除ボタン
            var delBtn = $(".actions button[data-name='delete_selected']");

            // 削除ボタンを表示する
            if (delBtn) {
                delBtn.show();
            }
            // 承認ボタン
            if (requestBtn) {
                requestBtn.show();
            }
            // 拒否ボタン
            if (denyBtn) {
                denyBtn.show();
            }
            // 貸出ボタン
            if (lendBtn) {
                lendBtn.show();
            }
            // 返済ボタン
            if (backBtn) {
                backBtn.show();
            }

            if (changeList) {
                flg = false;
                for (i = 0; i < changeList.length; i++) {
                    // 選択されているかを判断する
                    var selectedFlg = $(changeList[i]).find('tr').context.classList.contains('selected');

                    // 申請貸出状態
                    var lend_sts = $(changeList[i]).find("td[class='field-lend_status']").text()

                    // 報告状態が申請提出済の場合、返済と貸出ボタンを隠す
                    if (selectedFlg && lend_sts == '申請済'){
                        if (backBtn) {
                            backBtn.hide();
                        }
                        if (lendBtn) {
                            lendBtn.hide();
                        }
                        break;
                    }

                    // 報告状態が申請承認済の場合、返済ボタン、拒否ボタン、承認ボタンを隠す
                    if (selectedFlg && lend_sts == '承認済'){
                        if (backBtn) {
                            backBtn.hide();
                        }
                        if (denyBtn) {
                            denyBtn.hide();
                        }
                        if (requestBtn) {
                            requestBtn.hide();
                        }
                        break;
                    }

                    // 報告状態が貸出済の場合、貸出ボタン、拒否ボタン、承認ボタンを隠す
                    if (selectedFlg && lend_sts == '貸出済'){
                        if (lendBtn) {
                            lendBtn.hide();
                        }
                        if (denyBtn) {
                            denyBtn.hide();
                        }
                        if (requestBtn) {
                            requestBtn.hide();
                        }
                        break;
                    }

                    // 報告状態が返却済の場合、貸出ボタン、拒否ボタン、承認ボタン、返済ボタンを隠す
                    if (selectedFlg && lend_sts == '返却済'){
                        if (lendBtn) {
                            lendBtn.hide();
                        }
                        if (denyBtn) {
                            denyBtn.hide();
                        }
                        if (requestBtn) {
                            requestBtn.hide();
                        }
                        if (backBtn) {
                            backBtn.hide();
                        }
                        break;
                    }

                    // 報告状態が返却済の場合、貸出ボタン、拒否ボタン、承認ボタン、返却ボタンを隠す
                    if (selectedFlg && lend_sts == '拒否'){
                        if (lendBtn) {
                            lendBtn.hide();
                        }
                        if (denyBtn) {
                            denyBtn.hide();
                        }
                        if (requestBtn) {
                            requestBtn.hide();
                        }
                        if (backBtn) {
                            backBtn.hide();
                        }
                        break;
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