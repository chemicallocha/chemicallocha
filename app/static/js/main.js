$(document).foundation()

function addClass(e, cl){
    e.classList.add(cl);
}
function remClass(e, cl){
    e.classList.remove(cl);
}

function menu(x) {
    parent = x.parentNode
    if( parent.classList.contains('show-menu')){
        remClass(parent, 'show-menu');
        addClass(parent,'hide-menu');
        console.log('menu hidden');
    }
    else{
        remClass(parent, 'hide-menu');
        addClass(parent,'show-menu');
        console.log('showing menu')
    }
}
function showModal(modalID) {
    var modal = document.getElementById(modalID)
    
    if(modal.classList.contains('show-modal')){
        remClass(modal, 'show-modal');
        addClass(modal,'hide-modal');
        console.log('modal hidden');
    }
    else{
        addClass(modal, 'show-modal');
        remClass(modal,'hide-modal');
        console.log('showing-modal')
    }
}

$(document).ready(function(){
    // Add smooth scrolling to all links
    $("a").on('click', function(event) {

    // Make sure this.hash has a value before overriding default behavior
    if (this.hash !== "") {
        // Prevent default anchor click behavior
        event.preventDefault();

        // Store hash
        var hash = this.hash;

        // Using jQuery's animate() method to add smooth page scroll
        // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
        $('html, body').animate({
        scrollTop: $(hash).offset().top
        }, 800, function(){
    
        // Add hash (#) to URL when done scrolling (default click behavior)
        window.location.hash = hash;
        });
    } // End if
    });
});


