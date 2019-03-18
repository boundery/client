% rebase('base.tpl', title='Boundery.me')
<p>You'll need to go to boundery.me and create an account, or login if you already have one.  You can do so by <a onclick="document.forms['post_form'].submit(); return false;" href="">clicking here.</a></p>

<form id="post_form" method="post" action="{{central_url}}/accounts/client_enroll/" class="inline">
  <input type="hidden" name="port" value="{{port}}">
</form></p>
