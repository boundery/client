% rebase('base.tpl', title='Boundery.me')

<noscript>
  <div style="border: 1px solid purple; padding: 10px">
    <span style="color:red">JavaScript is not enabled!</span>
  </div>
</noscript>
<style>
  form {
    /* Just to center the form on the page */
    margin: 0 auto;
    /* To see the outline of the form */
    padding: 1em;
    border: 1px solid #CCC;
    border-radius: 1em;
  }

  form div + div {
    margin-top: 1em;
  }

  label {
    /* To make sure that all labels have the same size and are properly aligned */
    display: inline-block;
    width: 200px;
    text-align: right;
  }

  input, textarea {
    /* To make sure that all text fields have the same font settings
       By default, textareas have a monospace font */
    font: 1em sans-serif;

    /* To give the same size to all text fields */
    width: 300px;
    box-sizing: border-box;

    /* To harmonize the look & feel of text field border */
    border: 1px solid #999;
  }

  input:focus, textarea:focus {
    /* To give a little highlight on active elements */
    border-color: #000;
  }

  .button {
    /* To position the buttons to the same position of the text fields */
    padding-left: 200px; /* same size as the label elements */
  }

  button {
    /* This extra margin represent roughly the same space as the space
       between the labels and their text fields */
    margin-left: .5em;
  }


  .hideshow {
    display: none; _
  }
  input[type="radio"]:checked + .hideshow  {
    display: inline-block;
  }
}
</style>

<h1>Choose Wifi settings, then choose the device to use to create the boot card.</h1>

<p>If you are installing to a raspberry pi 3B (not 3B+), or any other computer that doesn't support 5GHz wifi, make sure to pick a 2.4GHz Wifi network.</p>

<form action="/step1" method="post">
  <div>
    <label for="ssid">Wifi Network Name (SSID):</label>
    <br>
    <div id="ssidlist">{{!ssidlist}}</div>
    <div>
      <input type="radio" name="ssid" value="__|other">Other <input class="hideshow" type="text" name="other_ssid" value=""><br>
    </div>
    <input type="radio" name="ssid" value="" required>None. I'm using wired ethernet.
  </div>
  <div>
    <label for="wifi_pw">Wifi Password (Leave blank for none):</label>
    <input type="text" name="wifi_pw" value="">
  </div>
  <br>
  <hr>
  <br>
  <div id="mountlist">{{!mountlist}}</div>
</form>

<script type="text/javascript">
  function poll1() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          var results = document.getElementById("mountlist");
          if (results.innerHTML != this.responseText) {
            results.innerHTML = this.responseText;
          }
        }
        setTimeout(poll1, 1000);
      }
    };
    xhr.open("GET", "/mounts", true);
    xhr.send();
  }
  function poll2() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          var results = document.getElementById("ssidlist");
          if (results.innerHTML != this.responseText) {
            results.innerHTML = this.responseText;
          }
        }
        setTimeout(poll2, 5000);
      }
    };
    xhr.open("GET", "/ssids", true);
    xhr.send();
  }
  function poll_all() {
    poll1()
    poll2()
  }
  window.onload = poll_all();
</script>
