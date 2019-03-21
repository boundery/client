% rebase('base.tpl', title='Boundery.me')

<noscript>
  <div style="border: 1px solid purple; padding: 10px">
    <span style="color:red">JavaScript is not enabled!</span>
  </div>
</noscript>

<div>
  <p id="msg">Writing to SD Card...</p>
  <progress id="progress"></progress>
</div>

<div id="done" style="display: none">
  <p>Safely eject the SD Card device, remove it from your computer, place it
    in the slot of your raspberry pi, and power on your raspberry pi.</p>
  <p>When you have done so, please <a href="/step2">click here.</a></p>
</div>

<script type="text/javascript">
  function poll1() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          data = JSON.parse(this.responseText);
          var progress = document.getElementById("progress");
          progress.max = data["max"];
          progress.value = data["cur"];
          if (progress.value == progress.max) {
            var msg = document.getElementById("msg");
            msg.innerHTML = "Finished writing to SD Card";

            var done = document.getElementById("done");
            done.style.display = "block";

            return;
          }
        }
        setTimeout(poll1, 1000);
      }
    };
    xhr.open("GET", "/step1_api2", true);
    xhr.send();
  }
  window.onload = poll1();
</script>
