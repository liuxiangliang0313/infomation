function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    //获取到edit,addtype标签
    var $a = $('.edit');
    var $add = $('.addtype');
    var $pop = $('.pop_con');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');
    var $input = $('.input_txt3');
    var sHandler = 'edit';
    var sId = 0;

    //判断是否点击了编辑
    $a.click(function(){
        sHandler = 'edit';
        sId = $(this).parent().siblings().eq(0).html();
        $pop.find('h3').html('修改分类');
        $pop.find('.input_txt3').val($(this).parent().prev().html());
        $pop.show();
    });

    //判断是否点击了增加
    $add.click(function(){
        sHandler = 'add';
        $pop.find('h3').html('新增分类');
        $input.val('');
        $pop.show();
    });

    $cancel.click(function(){
        $pop.hide();
        $error.hide();
    });

    $input.click(function(){
        $error.hide();
    });

    $confirm.click(function(){

        var params = {}
        //如果是编辑
        if(sHandler=='edit')
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            //拼接参数,编号,内容
            params = {
                "id": sId,
                "name": sVal,
            };
        }
        else
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            //拼接增加的名字
            params = {
                "name": sVal,
            }
        }

        // TODO 发起修改分类请求
        $.ajax({
            url:"/admin/add_category",
            method: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            contentType: "application/json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 刷新当前界面
                    location.reload();
                }else {
                    $error.html(resp.errmsg).show();
                }
            }
        })
    })
})