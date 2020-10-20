$(function () {
    const emptyMessage = "没有未读通知";
    const notice = $("#notifications");

    function CheckNotifications() {
        $.ajax({
            url: "/notifications/latest-notifications/",
            cache: false,
            success: function (data) {
                if (!data.includes(emptyMessage)){
                    notice.addClass("btn-danger")
                }
            },
        });
    };

    CheckNotifications();   // 页面加载时执行

    function update_social_activity(id_value){ // ajax更新相关数据（如点赞数）
        const newsToUpdate = $("[news-id=" + id_value + "]")
        $.ajax({
            url: "/news/update-interactions/",
            data: {"id_value": id_value},
            type: "POST",
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);

            }// end success
        });// end ajax
    }; // end function update_social_activity

    notice.click(function () {
        if ($(".popover").is(":visible")){
            notice.popover("hide");
            CheckNotifications();
        }else {
            notice.popover("dispose");
            $.ajax({
                url: "/notifications/latest-notifications/",
                cache: false,
                success: function (data) {
                    notice.popover({
                        html: true,
                        trigger: "focus",
                        container: "body",
                        placement: "bottom",
                        content: data
                    });
                    notice.popover("show");
                    notice.removeClass("btn-danger")
                },
            }); // end ajax
        }; // end else
        return false; // 直接弹框而不刷新加载新页面
    }); // end notice click function

    // websocket连接，使用wss(https)或者ws(http)
    const ws_scheme = window.location.protocol==="https" ? "wss" : "ws"
    const ws_path = ws_scheme + "://" + window.location.host + "/ws/notifications/";
    const ws = new ReconnectingWebSocket(ws_path);

    // 监听后端发送的数据
    ws.onmessage = function (event) {
        alert("?")
        const data = JSON.parse(event.data);
        alert(event.data())
        switch (data.key){
            case "notification": // 通知类型
                if (currentUser !== data.actor_name){ // 自己给自己点赞不提示
                    notice.addClass("btn-danger");
                }
                break;
            case "social_update": // 通知类型且需要ajax更新赞数/评论数
                if (currentUser !== data.actor_name){ // 自己给自己点赞不提示
                    notice.addClass("btn-danger");
                };
                update_social_activity(data.id_value); // ajax更新相关网页，比如点赞数
                break;
            case "additional_news": // 新动态
                alert("additional_news");
                if (currentUser !== data.actor_name){ // 自己给自己点赞不提示
                    $(".stream-update").show();
                }
                break;
            default:
                console.log("error", data);
                break;
        }
    }


});
