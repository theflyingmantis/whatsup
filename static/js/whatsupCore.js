var key = "somethingRandom";
var TIMEOUT = "3000";
var URL = "checkforchange?key="
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
            console.log("Something went wrong");
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
    for (var i = 0; i < slides.length; i++) {
        // inflating logic here based on css
        if (slides[i].type == "just-text") {
            createSimpleSlide(slides[i])
        }
        if (slides[i].type == "text-and-image") {
            createTextAndImageSlide(slides[i])
        }

    }
}

function createTextAndImageSlide(slideData) {
    var slide = document.createElement("div");
    slide.className = "slide";
    if (slideData["background_color"] != "") {
        slide.style.backgroundColor = slideData["background_color"];
    }
    if (slideData["background_image_url"] != "") {
        slide.style.backgroundImage = "url(" + slideData["background_image_url"]+")"
    }
    // condition for image
    document.getElementById("main").appendChild(slide);

    if (slideData["text"] != "") {
        var header = document.createElement("div");
        header.className = slideData["type"];
        slide.appendChild(header);
        var img = document.createElement("img");
        img.src = slideData["image_url"];
        header.appendChild(img);
        var para = document.createElement("p");
        para.innerHTML = slideData["text"];
        header.appendChild(para);
    }
}

function createSimpleSlide(slideData) {
    var slide = document.createElement("div");
    slide.className = "slide";
    if (slideData["background_color"] != "") {
        slide.style.backgroundColor = slideData["background_color"];
    }
    if (slideData["background_image_url"] != "") {
        slide.style.backgroundImage = "url(" + slideData["background_image_url"]+")"
    }
    // condition for image
    document.getElementById("main").appendChild(slide);

    if (slideData["text"] != "") {
        var header = document.createElement("div");
        header.className = slideData["type"];
        slide.appendChild(header);
        var para = document.createElement("p");
        para.innerHTML = slideData["text"];
        header.appendChild(para);
    }

}

var slideNumber = 0;


function scrolling(finalResult) {
    scrollingTimeout = setTimeout(function() {
        myFullpage.moveSlideRight()
        slideNumber += 1
        scrolling(finalResult)
    }, finalResult[slideNumber % finalResult.length]["time"])
}