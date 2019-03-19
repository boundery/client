<label>Choose your SD Card:</label>
% for mount in mounts:
<div class="button">
  <button name="mount" value="{{mount}}">Write to {{mount}}</button>
</div>
% end
