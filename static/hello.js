window.onload= function () {
    document.getElementById('welcome').style.display= "block";
    openSignup();
}

  function openSignup() {
    setTimeout(() => {
      window.location.href = "/register";
    }, 4000);
  }

/*
alert('hiiiii')
*/