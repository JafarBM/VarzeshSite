let IDEs = {};

$("[id^=code-form-]").each(function () {
    let problemId = $(this).attr("id").substring(10);
    IDEs[problemId] = CodeMirror.fromTextArea($(this).closest("textarea")[0], {
        mode: "text/x-csrc",
        styleActiveLine: true,
        matchBrackets: true,
        lineNumbers: true,
    });
    IDEs[problemId].on("change", function (cm, change) {
        cm.save()
    });

});

$("[id^=select-theme-]").on("change", function () {
    let problemId = $(this).attr("id").substring(13);
    let theme = $(this).find("option:selected").val();
    IDEs[problemId].setOption("theme", theme);
    location.hash = "#" + theme;
});

$("[id^=select-lang-]").on("change", function () {
    let problemId = $(this).attr("id").substring(12);
    let language = $(this).find("option:selected").val();
    let ide = IDEs[problemId];

    if (language === "C" || language === "C++") {
        ide.setOption("mode", "text/x-csrc");
        ide.setOption("indentUnit", 2);
    }
    if (language === "Python2") {
        ide.setOption("mode", {
            name: "python",
            version: 2,
            singleLineStringErrors: false
        });
        ide.setOption("indentUnit", 4);
    }
    if (language === "Python3") {
        ide.setOption("mode", {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        });
        ide.setOption("indentUnit", 4);

    }

    location.hash = "#" + language;
});


for (let problemId in IDEs) {
    if (IDEs.hasOwnProperty(problemId)) {
        $(`[id^=select-theme-${problemId}]`).val("eclipse").change();
    }
}


$("form.test-case-ajax").on('submit', function (event) {
    event.preventDefault();
    let dataDict = objectifyForm($(this).serializeArray());
    let formData = new FormData(this);
    let form = $(this);
    let targetUrl = $(this).data('url');
    $.ajax({
        type: "POST",
        url: targetUrl,
        data: formData,
        dataType: 'json',
        cache: false,
        contentType: false,
        processData: false
    }).done(function (data) {
        if (data.success === true) {
            let index = $('div.test-case').length + 1;
            let is_sample = dataDict.is_sample ? '<small>(تست کیس نمونه)</small>' : '';
            $('#accordion').append(
                `
                <div class="card test-case">
                    <div class="card-header">
                        <div class="row">
                            <div class="col-3 d-flex align-items-center">
                                <button class="remove-testcase btn btn-sm ml-2" type="button" data="${data.testcase_id}" data-url="${targetUrl}">
                                    <i class="fa fa-trash"></i>    
                                </button>
                                <a class="card-link unload" data-toggle="collapse"
                                   href="#collapse-${data.testcase_id}">
                                    تست کیس ${index}
                                </a>
                            </div>
                            <div class="col-3 d-flex align-items-center">
                                <a href="${data.input_upload_to}"
                                   class="input-link btn btn-info btn-sm" role="button">ورودی
                                    <i
                                            class="fa fa-file-download"></i></a>
                            </div>
                            <div class="col-3 d-flex align-items-center">
                                <a href="${data.output_upload_to}"
                                   class="output-link btn btn-info btn-sm" role="button">خروجی
                                    <i
                                            class="fa fa-file-download"></i></a>
                            </div>
                            <div class="col-3">
                                ${is_sample}
                            </div>
                        </div>
                    </div>
                    <div id="collapse-${data.testcase_id}" class="collapse" data-parent="#accordion">
                        <div class="card-body">
                            <div class="row">
                                <div class="input-load col-md-6">
                                    <i class="fa fa-spin fa-spinner float-right m-1"></i>
                                    <h6>ورودی:</h6>
                                    <div align="left" class="shadow-sm p-4 mb-4 bg-light">
                                        <pre></pre>
                                    </div>
                                </div>
                                <div class="output-load col-md-6">
                                    <i class="fa fa-spin fa-spinner float-right m-1"></i>
                                    <h6>خروجی:</h6>
                                    <div align="left" class="shadow-sm p-4 mb-4 bg-light">
                                        <pre></pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                `
            );
            form.trigger('reset');
        } else {
            alert(JSON.stringify(data));
        }
    });
});

function objectifyForm(formArray) {

    let returnArray = {};
    for (let i = 0; i < formArray.length; i++) {
        returnArray[formArray[i]['name']] = formArray[i]['value'];
    }
    return returnArray;
}

$(document).on('click', '#testCases [data-toggle="collapse"].unload', function (event) {
    let firstLoad = false;
    let href = $(this).attr('href');
    $(`${href} .input-load pre`).load($(this).closest('.card').find('.input-link').attr('href'),
        function () {
            let autoHeight = $(this).css('height', 'auto').height();
            $(this).height(0).animate({height: autoHeight}, 1000, function () {
                $(this).height('auto')
            });
            $(this).closest('.input-load').find('i.fa.fa-spin').fadeOut();
            if (!firstLoad) {
                firstLoad = true;
            } else {
                $(`[href='${href}']`).removeClass("unload");
            }
        });
    $(`${href} .output-load pre`).load($(this).closest('.card').find('.output-link').attr('href'),
        function () {
            let autoHeight = $(this).css('height', 'auto').height();
            $(this).height(0).animate({height: autoHeight}, 1000, function () {
                $(this).height('auto')
            });
            $(this).closest('.output-load').find('i.fa.fa-spin').fadeOut();
            if (!firstLoad) {
                firstLoad = true;
            } else {
                $(`[href='${href}']`).removeClass("unload");
            }
        });
});

$.fn.log = function () {
    console.log.apply(console, this);
    return this;
};

$('form#testCase a[data-toggle="pill"]').on('click', function () {
    let allTabs = $(`${$(this).attr('href')}`).parent();
    allTabs.find('textarea').val('');
    allTabs.find('input').val('');
});

submitError = {
    CompileError: 'خطای کامپایل'
};

contextClass = {
    WRONG_ANSWER: 'danger',
    SUCCESS: 'success',
    CPU_TIME_LIMIT_EXCEEDED: 'warning',
    REAL_TIME_LIMIT_EXCEEDED: 'warning',
    MEMORY_LIMIT_EXCEEDED: 'warning',
    RUNTIME_ERROR: 'info',
    SYSTEM_ERROR: 'info',
};

$("form[id^='form-']").on("submit", function (event) {
    let form = $(this).closest("form");
    let problemId = $(this).attr("id");
    problemId = problemId.substring(5);
    IDEs[problemId].save();
    let status = $(`#submission-status-${problemId}`);
    let preloader = status.find('.preloader');
    let results = status.find('.result');
    results.animate({"opacity": 0});
    preloader.animate({"opacity": 1});
    event.preventDefault();
    let $this = $(this);

    $.ajax({
        url: form.data('url'),
        data: form.serialize(),
        dataType: 'json',
        type: 'POST',
    }).done(function (data) {
            console.log(data)
            preloader.animate({"opacity": 0});
            results.html('');
            if (data['is_submitted']) {
                if (data['error'] == null) {
                    let accepted = 0;
                    let list = results.append('<ul class="list-group"></ul>').find('ul');
                    if(data['got_credit']) {
                        results.append(`<br> <h6> ${data['credit_amount']} امتیاز به امتیازات شما اضافه شد! </h6>`)
                        let creditHtml = "امتیاز: " + data['credit'] + `<i class="fas fa-award"></i>`;
                        $("#credit").html(creditHtml);
                    }
                    for (let i = 0; i < data['test_cases'].length; i++) {
                        let testCase = data['test_cases'][i];
                        console.log(testCase);
                        if (testCase['result'] === 'SUCCESS') {
                            accepted++;
                        }
                        let downloadLink;
                        if (testCase['has_access']){
                            downloadLink = `<div class="col-3">
                                        <a href="${testCase['input_file']}"
                                           class="input-link btn btn-info btn-sm" role="button">ورودی
                                            <i
                                                    class="fa fa-file-download"></i></a>
                                    </div>
                                    <div class="col-3">
                                        <a href="${testCase['output_file']}"
                                           class="output-link btn btn-info btn-sm" role="button">خروجی
                                            <i
                                                    class="fa fa-file-download"></i></a>
                                    </div> `
                        }else {
                            downloadLink = `<div class="col-6"><a> 
                                                <button class="buy-test-case btn btn-primary btn-sm" type="button" data-uuid="${testCase['uuid']}" data-url="/exercise/problems/${problemId}/buy-test-case/">
                                                    <i class="fas fa-unlock ml-1"></i></a>
                                                    باز کردن تست کیس  
                                                </button>
                                            </div>
                                            <div class="col-3 input-file d-none" id="input-${testCase['uuid']}">
                                            <a href="${testCase['input_file']}"
                                               class="input-link btn btn-info btn-sm" role="button">ورودی
                                                <i
                                                        class="fa fa-file-download"></i></a>
                                            </div>
                                            <div class="col-3 output-file d-none" id="output-${testCase['uuid']}">
                                                <a href="${testCase['output_file']}"
                                                   class="output-link btn btn-info btn-sm" role="button">خروجی
                                                    <i
                                                            class="fa fa-file-download"></i></a>
                                            </div> `
                        }
                        list.append(`
                            <li class="list-group-item" style="display: none;">
                                <div class="row">
                                    <div class="col-3">
                                        تست کیس ${i + 1}
                                    </div>
                                    ${downloadLink}
                                    <div class="col-3">
                                        <span class="badge badge-${contextClass[testCase['result']]} badge-pill float-right">${testCase['result'].split('_').join(' ')}</span>
                                    </div>
                                </div>
                            </li>
                        `);

                        list.find('li:last-child').delay(i * 250).fadeIn(250);
                    }
                    if (accepted !== data['test_cases'].length) {
                        results.prepend(`<h4>${data['test_cases'].length - accepted} تست کیس از ${data['test_cases'].length} تا ناموفق بود!</h4>`)
                    } else {
                        var elementExists = $('#feedbackModal');
                        if (elementExists !== null ) {
                            if (data['is_passed'] == false) {
                                elementExists.modal('show');
                            }
                        }
                        results.prepend(`<h4>تبریک! تمام تست کیس‌ها با موفقیت پاس شدند!</h4>`)
                    }
                } else {
                    results.prepend(`<h4>${submitError[data['error']]}</h4>`);
                }
            } else {
                results.prepend(`<h4>کد شما ثبت نشد، لطفاً دوباره تلاش کنید.</h4>`);
            }
            results.animate({"opacity": 1});
            let collapse = $this.closest("div[id^='collapse-']").attr("id");
            let quizDiv = $("div[id^='Quiz-']");
            if (quizDiv.length) {
                let quizId = quizDiv.attr("id").substring(5);
                if (data['is_correct']) {
                    $(`[href="#${collapse}"] div.card-header`).attr("class", "card-header quiz-problem-correct")
                } else {
                    $(`[href="#${collapse}"] div.card-header`).attr("class", "card-header quiz-problem-wrong")
                }
                checkEndQuiz(quizId).done(function (data) {
                    if (data['is_completed']) {
                        $("#completedModal").modal();
                    }
                });
            }
        }
    );
});


$(document).on('click', ".buy-test-case", function (event) {
    console.log("IN BUY TEST CASE")
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    console.log($(this).data('url'));
    console.log($(this).data('uuid'));
    let $this = $(this);
    $.ajax({
        type: "POST",
        url: $(this).data('url'),
        dataType: 'json',
        data: $(this).data('uuid')
    }).done(function (data) {
        if (data['has_enough_credit']) {
            $this.closest(".col-6").addClass("d-none");
            let creditHtml = "امتیاز: " + data['credit'] + `<i class="fas fa-award"></i>`;
            $("#credit").html(creditHtml);
            $(`#input-${$this.data('uuid')}`).removeClass("d-none");
            $(`#output-${$this.data('uuid')}`).removeClass("d-none");
        }else {
            window.alert("برای این کار امتیاز کافی ندارید.")
        }
    })
});

function checkEndQuiz(quizId) {
    return $.ajax({
        url: "/exercise/quiz/" + quizId + "/check/",
        dataType: 'json',
    });
}


$.fn.timer = function () {
    let deadline = new Date(Number($(this).data('deadline')));
    $.fn.showDeadline = function () {
        let hours = Math.floor((deadline % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((deadline % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((deadline % (1000 * 60)) / 1000);

        // Display the result in the element with id="demo"
        $(this).html(`${hours} ساعت و ${minutes} دقیقه و ${seconds} ثانیه`);

        // If the count down is finished, write some text
        if (deadline < 0) {
            $(this).html("این سؤالات برای دیروز اند.");
        }
        deadline -= 1000;
    };
    $(this).showDeadline();
    setInterval($.fn.showDeadline.bind($(this)), 1000);
};

$('#daily-challenge-timer').timer();


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');
let infoModal = $('#myModal');
$(document).on('click', '.submission_btn', function (event) {
    event.preventDefault();
    subid = $(this).attr('subid');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        url: '/exercise/submissions/' + subid + '/',
        data: {'id': subid},
        dataType: 'json',
        type: "POST",
        success: function (data) {
            d = JSON.stringify(data)
            let item = JSON.parse(d);
            let src_code = "<br>" + item.src_code.replace(/\n/g, "<br>")

            let htmlData = '<code dir="ltr">';
            htmlData += src_code;
            htmlData += '</code>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.find('.modal-title').html('ارسال' + subid)
        }
    });
    infoModal.modal();
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).on('click', "button[class^='remove-testcase']", function (event) {
    event.preventDefault();
    let testCaseId = $(this).data("id");
    let removeDiv = $(this);
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        type: "DELETE",
        url: $(this).data('url'),
        data: testCaseId,
        dataType: 'json',
    }).done(function (data) {
        if (data['success']) {
            let row = removeDiv.closest('div.test-case')
            row.fadeOut('slow', function () {
                $(this).remove();
            });
        }
    })
});

$("button[class^='remove-problem']").on('click', function (event) {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        type: "DELETE",
        url: $(this).data('url'),
        dataType: 'json',
    }).done(function (data) {
        if (data['success']) {
            $("#deleteModal").modal();
        }
    })
});
