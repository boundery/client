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
</style>

<p>Choose Wifi settings, then choose the device to use to create the boot card.</p>

<form action="/step1" method="post">
  <div>
    <label for="ssid">Wifi Network Name (SSID):</label>
    <input type="text" name="ssid" value="">
  </div>
  <div>
    <label for="wifi_pw">Wifi Password (Blank for none):</label>
    <input type="text" name="wifi_pw" value="">
  </div>
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
    xhr.open("GET", "/step1_api1", true);
    xhr.send();
  }
  window.onload = poll1();
</script>