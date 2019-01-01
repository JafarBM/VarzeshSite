started_date = document.getElementById("start_date");
is_finished = document.getElementById("is_finished");
let courseTimer = document.getElementById("course-timer");
if (courseTimer) {

    let x = setInterval(function () {
        let now = new Date().getTime();
        let distance = now - started_date.value * 1000;

        let days = Math.floor(distance / (1000 * 60 * 60 * 24));
        let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if (days === 0) {
            if (hours === 0) {
                if (minutes === 0)
                    courseTimer.innerHTML = seconds + "S ";
                else
                    courseTimer.innerHTML = minutes + "M " + seconds + "S ";
            }
            else
                courseTimer.innerHTML = hours + "H " + minutes + "M " + seconds + "S ";
        }
        else
            courseTimer.innerHTML = days + "D " + hours + "H " + minutes + "M " + seconds + "S ";


        if (is_finished.value === "True") {
            clearInterval(x);
            courseTimer.innerHTML = "اینجا کارت تموم شده !";
        }

    }, 1000);
}