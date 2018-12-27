started_date = document.getElementById("start_date");
is_finished = document.getElementById("is_finished");
raw_start_date = started_date.value.toString();
let is_pm = false;
if (raw_start_date.substr(raw_start_date.length - 4, raw_start_date.length - 1) === 'p.m.'){
    is_pm = true;
}
const start_date = started_date.value.toString().replace('p.m.', '').replace('a.m.', '').slice(0, -1).replace('.', '') + ":00";
const countDownDate = new Date(start_date).getTime();

let x = setInterval(function () {
    let now = new Date().getTime();
    let distance = now - countDownDate;

    let days = Math.floor(distance / (1000 * 60 * 60 * 24));
    let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    if (is_pm && hours >= 12){
        hours -= 12;
    }
    let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if(days === 0){
        if(hours === 0) {
            if(minutes === 0)
                document.getElementById("timer").innerHTML = seconds + "S ";
            else
                document.getElementById("timer").innerHTML = minutes + "M " + seconds + "S ";
        }
        else
            document.getElementById("timer").innerHTML = hours + "H " + minutes + "M " + seconds + "S ";
    }
    else
        document.getElementById("timer").innerHTML = days + "D " + hours + "H " + minutes + "M " + seconds + "S ";



    if (is_finished.value === "True") {
        clearInterval(x);
        document.getElementById("timer").innerHTML = "اینجا کارت تموم شده :))!";
    }

}, 1000);