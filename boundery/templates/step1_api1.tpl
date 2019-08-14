<label>Choose your SD Card:</label>
% for mount in mounts:
<div class="button">
  <button name="mount" value="{{mount[1]}}">Write to {{mount[0]}} ({{mount[1]}})</button>
</div>
% end
