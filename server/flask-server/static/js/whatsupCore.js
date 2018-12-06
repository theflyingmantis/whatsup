var key = "somethingRandom";
var TIMEOUT = "3000";
var URL = "http://localhost:5000/checkforchange?key="
var scrollingTimeout;


function removeChildOfMain() {
    var root = document.getElementById("main");
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
    clearTimeout(scrollingTimeout)
}

function checkForChange() {
    $.ajax({
        url: URL + key,
        crossDomain: true,
        dataType: 'json',
        success: function(result) {
            key = result["key"];
            if (result["isChanged"] == true) {
                removeChildOfMain()
                inflateView(result["data"])
                loadFullPage()
                scrolling(result["data"])
            }
        },
        error: function(textStatus, errorThrown) {
            alert("Something went wrong");
        }
    });
}

performCheckEveryPeriod()
function performCheckEveryPeriod() {
	checkForChange()
	setInterval(
	    function() {
	        checkForChange()
	    },
	    TIMEOUT
	);
} 


function inflateView(slides) {
    console.log(slides)
    for (var i = 0; i < slides.length; i++) {
        // inflating logic here based on css
        if (slides[i].type == "just-text") {
            createSimpleSlide(slides[i])
        }

    }
}

function createSimpleSlide(slideData) {
    var slide = document.createElement("div");
    slide.className = "slide";
    slide.style.backgroundColor = slideData["background_color"];
    // condition for image
    document.getElementById("main").appendChild(slide);

    var header = document.createElement("div");
    header.className = slideData["type"];
    slide.appendChild(header);

    var para = document.createElement("p");
    para.innerHTML = slideData["text"];
    header.appendChild(para);
}

var slideNumber = 0;


function scrolling(finalResult) {
    scrollingTimeout = setTimeout(function() {
        myFullpage.moveSlideRight()
        slideNumber += 1
        scrolling(finalResult)
    }, finalResult[slideNumber % finalResult.length]["time"])
}