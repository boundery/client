% for ssid in ssids:
% if ssid[2]:
<input type="radio" name="ssid" value="={{ssid[1]}}" checked="checked">{{ssid[0]}}<br>
% else:
<input type="radio" name="ssid" value="={{ssid[1]}}">{{ssid[0]}}<br>
% end
% end
