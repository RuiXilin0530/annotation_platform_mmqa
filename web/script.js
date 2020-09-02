
var username = '';
var password = '';

var login_status = false;

var SENT_UNLABELED = "content-sent-unlabeled";
var SENT_SELECTED = "content-sent-selected";
var SENT_LABELED = "content-sent-labeled";

// Global variable
var page_data;
var parallel_pairs = Array();

function refresh_page() {
    parallel_pairs = Array();
    $('textarea').val('');
}

$(document).ready(build_web);

function build_web(){
    $("button.login").click(open_login_window); //class
    $('.theme-poptit .close').click(close_login_window);
    $('.theme-signin').submit(submit_authentication);

    $("#btn_refresh").click(get_data); //id
    $("#btn_submit").click(pop_confirm_window);
    $(".pop-window.confirm .close").click(close_confirm_window);

    $("*[name='btn_select']").click(func_btn_select); //属性选择器
    $("*[name='btn_back']").click(func_btn_back);

    // $(window).scroll(scroll_listener);
    refresh_page();

}

function scroll_listener(e) {
    var fix_btn = $(".table-btn.fixed");
    var float_btn = $(".table-btn.float");

    var win_h = document.body.clientHeight;
    var fix_pos = fix_btn.offset().top;
    var win_scroll = document.body.scrollTop;

    if (fix_pos - win_scroll < win_h/10) {
        if (float_btn.css("visibility") != "visible") {
            float_btn.css('visibility', 'visible');
            float_btn.find('.status').css('visibility', fix_btn.find('.status').css("visibility"))
        }
    }
    else {
        if (float_btn.css("visibility") != "hidden") {
            float_btn.css('visibility', 'hidden');
            fix_btn.find('.status').css("visibility", float_btn.find('.status').css('visibility'))
            float_btn.find('.status').css("visibility", 'hidden')
        }
    }
}

function open_login_window(){
    $('.theme-signin .login-status').css('visibility', 'hidden');
    $(".login-window-shadow").fadeIn(200);
    $(".pop-window.login").slideDown(200);
}

function close_login_window(){
    $('.login-window-shadow').fadeOut(100);
    $('.pop-window.login').slideUp(100);
}

function pop_confirm_window() {
    var msg = null;
    $(".pop-window.confirm button").unbind();
    if ($(this).attr("id") == "btn_submit"){
        $(".pop-window.confirm .msg").html("confirm to <b>submit </b>the data?");
        $(".pop-window.confirm button").click(submit_data);
    }

    $(".pop-window.confirm .status").css("visibility", "hidden")

    $(".login-window-shadow").fadeIn(200);
    $(".pop-window.confirm").slideDown(200);
}

function close_confirm_window() {
    $(".login-window-shadow").fadeOut(200);
    $(".pop-window.confirm").slideUp(200);
}

function submit_authentication(event){
    event.preventDefault();
    username = $(".theme-signin input[name='user']").val();
    password = $(".theme-signin input[name='pwd']").val();
    var req_data = {user: username,password: password};
    $.ajax({
        url: "authentication",
        type: "POST",
        data: JSON.stringify(req_data),
        contentType: "application/json",
        success: response_authentication,
    })
}

function response_authentication(data, status){
    if(data.status == 100){
        $("#user_name_display").text("welcome: " + username)
        close_login_window()
        $(".content-bilingual").css("border", "2px solid #626567")
        get_data()
    }
    else{
        $('.theme-signin .status.login').css('visibility', 'visible');
        $("#user_name_display").text("未登录")
    }
}

function get_data() {
    var req_data = {user: username, password: password};
    $.ajax({
        url: "get-data",
        type: "POST",
        data: JSON.stringify(req_data),
        contentType: "application/json",
        success: populate_content
    })
    refresh_page()
}

function populate_content(res_data) {
    var status = res_data.status;
    if (status >= 200){
        $(".status.data-req").text(res_data.status_text);
        $(".status.data-req").css("visibility", "visible");
        page_data = null;
    }
    else if (status==100){
        $(".status.data-req").text("");
        $(".status.data-req").css("visibility", "hidden"); 

        $(".status.select").css("visibility", "hidden"); //请至少在每个领域选择一个句子 需要改

        page_data = res_data.data;
        var pid = page_data.id;
        // var title = page_data.title;
        var pass_context = page_data.html_text;
        var pass_start = page_data.html_start;
        var pass_qa = page_data.qas;
        var url_image = page_data.url;
        $("#pid").text("ID： " + pid)
        // $("#page_name").text(title[0])
        // $("#page_section").text(title[1])
        // $("#page_cat").html(title[2] + "<br>" + title[3])

        var medical_container = $(".content-bilingual.medical");
        var health_container = $(".content-bilingual.health");

        fill_context(medical_container, pass_context, pass_start, pass_qa, url_image);
        fill_qa(health_container, pass_qa);
    }
}

function fill_context(container, context, pass_start, pass_qa, url){
    container.empty()
    var en_sent = $("<div></div>").attr("class", "sent-en");
    // var img_box = $("<img>").attr("width", "300");
    var img_box = $('<img>');
    img_box.attr("width", "300");
    for(var i = 0; i< context.length; i++)
    {
        var a = context[i];
        for(var j=0; j<pass_start.length; j++)
        {
            a = a.replaceAll(pass_qa[j].answers[0].text, "<span style=\"color:blue\">" + pass_qa[j].answers[0].text + "</span>");
            // console.log(a);
            // console.log(pass_qa[j].answers[0].answer_start);
            // console.log(pass_qa[j].answers[0].text);
        }
        en_sent.html(a);
        container.append((en_sent.clone(true)));
        container.append('<br>');
    }
    // en_sent.html(en_sent.html().replace("woman", <span style="color:blue">woman</span>))
    for(var i=0; i<url.length; i++){
        img_box.attr("src", url[i]);
        container.append(img_box.clone(true));
    }
}

function fill_qa(container, data){
    container.empty()
    // var sent_box = $("<div></div>").attr("class", "content-sent-unlabeled");
    var en_sent1 = $("<div></div>").attr("class", "sent-en-red");
    var en_sent2 = $("<div></div>").attr("class", "sent-en-blue");
    var en_sent3 = $("<div></div>").attr("class", "sent-en");
    var input_box = $('<input>');
    var br_box = $('<br>');
    input_box.attr("type", "radio");
    var text_box = $('<input>');
    text_box.attr("type", "text");
    text_box.attr("size", "60");
    text_box.attr("style", "font-size:16px");

    // sent_box.click(sent_click);
    for (var i=0; i<data.length; i++){
        en_sent1.text("Question: " + data[i].question);
        container.append(en_sent1.clone(true));
        en_sent1.text("Answer: " + data[i].answers[0].text);
        container.append(en_sent1.clone(true));
        en_sent2.text("Arguement role: " + data[i].arguement);
        container.append(en_sent2.clone(true));
        en_sent3.text("Does the question need to modify the gram");
        container.append(en_sent3.clone(true));
        input_box.attr("name", data[i].id);
        input_box.attr("value", "correct");
        // input_box.text("Correct");
        container.append(input_box.clone(true));
        container.append("Correct</br>");
        container.append(br_box);
        input_box.attr("name", data[i].id);
        input_box.attr("value", "question");
        container.append(input_box.clone(true));
        container.append("Need to modify the question</br>");
        container.append(br_box);
        // input_box.text("Need to modify the question");
        input_box.attr("name", data[i].id);
        input_box.attr("value", "answer");
        container.append(input_box.clone(true));
        container.append("Need to modify the answer</br>");
        container.append(br_box);
        // input_box.text("Need to modify the answer");
        input_box.attr("name", data[i].id);
        input_box.attr("value", "wrong");
        container.append(input_box.clone(true));
        container.append("Absolutely wrong</br>");
        container.append(br_box);
        // input_box.text("Absolutely wrong");
        text_box.attr("name", data[i].id);
        text_box.attr("value", "None");
        container.append(text_box.clone(true));
        container.append(br_box);

        en_sent3.text("Is the question and answer related to pictures?");
        container.append(en_sent3.clone(true));
        input_box.attr("name", data[i].id + "image");
        input_box.attr("value", "related to pirctures");
        container.append(input_box.clone(true));
        container.append("related to pirctures</br>");
        container.append(br_box);
        input_box.attr("name", data[i].id + "image");
        input_box.attr("value", "not related to pirctures");
        container.append(input_box.clone(true));
        container.append("not related to pirctures</br></br>");
        container.append(br_box);
    }
}


function update_input_box(p_cls) {
    var domain = null;
    if (p_cls.indexOf('medical') >=0){
        domain = 'medical';
    }
    else {
        domain = 'health';
    }
    t = $(".content-bilingual."+domain).children("."+SENT_SELECTED).children(".sent-en").text();
    $('.'+domain+" textarea").val(t);
}

function func_btn_select() {
    var medical_sentid = scan_selected_sent($(".content-bilingual.medical").children());
    var health_sentid = scan_selected_sent($(".content-bilingual.health").children());
    if (medical_sentid.length == 0 || health_sentid.length == 0){
        $(this).parent().parent().find('.status').css("visibility", "visible");
    }
    else {
        $(this).parent().parent().find('.status').css("visibility", "hidden");
        
        change_sent_status($(".content-bilingual.medical").children(), medical_sentid, SENT_LABELED);
        change_sent_status($(".content-bilingual.health").children(), health_sentid, SENT_LABELED);

        e_sent = $(".medical textarea").val()
        ne_sent = $(".health textarea").val()
        parallel_pairs.push({
            medical: medical_sentid, health: health_sentid,
            e_sent: e_sent, ne_sent: ne_sent
        });
        $("textarea").val('');
    }
}

function scan_selected_sent(content){
    var selected = [];
    for (var i=0; i<content.length; i++){
        if (content[i].getAttribute("class") == SENT_SELECTED){
            selected.push(parseInt(content[i].getAttribute("data-sentid")));
        }
    }
    return selected
}

function change_sent_status(content, ids, status){
    var s_id = null;
    for (var i=0; i<content.length; i++){
        s_id = parseInt(content[i].getAttribute("data-sentid"));
        if (ids.indexOf(s_id) > -1){
            content[i].setAttribute("class", status)
        }
    }
}

function func_btn_back() {
    $(this).parent().parent().find('.status').css("visibility", "hidden");
    if (parallel_pairs.length > 0){
        var pair = parallel_pairs.pop()
        change_sent_status($(".content-bilingual.medical").children(), pair.medical, SENT_UNLABELED);
        change_sent_status($(".content-bilingual.health").children(), pair.health, SENT_UNLABELED);
    }
}

function submit_data(){
    var text = Array();
    var select = Array();
    var image = Array();
    child = $(".content-bilingual.health input")
    child.each(function(i)
    {
        if(i%7 == 4)
        {
            text.push(this.value);
        }
        if(this.checked)
        {
            if(i%7 > 4)
            {
                image.push(i%7-5);
            }
            else
            {
                select.push(i%7)
            }
        }
    })
    var req_data = {
        id:        page_data.id, 
        user:       username,
        password:   password,
        label_result:   {text:text, select:select, image:image}};
    var flag = 0;
    for(var i=0; i < text.length; i++)
    {
        if(select[i] != 0 & text[i] == 'None')
        {
            flag = 1;
        }
        if(select[i] == 0 & text[i] != 'None')
        {
            flag = 1;
        }
        if(select[i] == 3 & text[i].length < 50)
        {
            flag = 1;
        }
    }
    if(image.length != text.length)
    {
        flag = 1;
    }
    if(flag == 0)
    {
        $.ajax({
            url: "send-data",
            type: "POST",
            data: JSON.stringify(req_data),
            contentType: "application/json",
            success: response_submit
        })
    }
}

function response_submit(data){
    if (data.status == 100){
        $(".pop-window.confirm .status").css("visibility", "hidden")
        close_confirm_window();
        get_data();
        refresh_page();
    }
    else {
        $(".pop-window.confirm .status").text(data.status_text);
        $(".pop-window.confirm .status").css("visibility", "visible");
    }
}
