% rebase('base.tpl', title='Boundery.me')
<p>Installing</p>
<div id="results"><p style="color:orange">Waiting for home server to register itself.</p></div>
<div id="storelink"></div>

%#XXX Need to detect if Javascript is off, and warn appropriately
<script type="text/javascript">
  function poll1() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          var results = document.getElementById("results");
          results.innerHTML = "<p style=\"color:orange\">Trying to contact home server.</p>";
          poll2();
        } else {
          setTimeout(poll1, 5000);
        }
      }
    };
    xhr.open("POST", "/step4_api1", true);
    xhr.send();
  }

  function poll2() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          var results = document.getElementById("results");
          results.innerHTML = "<p style=\"color:orange\">Joining secure network.</p>";
          poll3();
        } else {
          //Short timeout, because api2 has its own timeout.
          setTimeout(poll2, 500);
        }
      }
    };
    xhr.open("POST", "/step4_api2", true);
    xhr.send();
  }

  function poll3() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          var results = document.getElementById("results");
          results.innerHTML = "<p style=\"color:green\">Joined secure network.</p>";
          var storelink = document.getElementById("storelink");
          storelink.innerHTML = "<p><a href=\"{{central_url}}/apps/store\">Click here</a> to go the app store.</p>"
        } else {
          setTimeout(poll3, 1000);
        }
      }
    };

    xhr.open("POST", "/step4_api3", true);
    xhr.send();
  }

  window.onload = poll1();
</script>
