<!-- images, prev_page_num, next_page_num, move_dir, -->
  <html>
  <head>
    <script type="text/javascript" src="http://gettopup.com/releases/latest/top_up-min.js"></script>
  </head>
  <body>
  <a href="/p/{{prev_page_num}}">Prev</a><br>
  <a href="/p/{{next_page_num}}">Next</a><br>
  <table>
    %for x in images:
      <tr>
	<td><a href="/image/i/{{x}}" class="top_up" target="_blank">
	    <img src="/image/t/{{x}}" style="height:50;max-width:100"/></a></td>
	%if movedir is not None:
   	  <td>
	    <input IMG="{{x}}" 
		   class="move_button" style="height:30" type="submit" 
		   value="Move to {{movedir}}">
	  </td>
        %end
	<td>{{x}}</td>
      </tr>
    %end
  </table>
  
  <script type="text/javascript">
    // Use jQuery to handle moving images
    $("input.move_button").click(function () {
	var td = this
	var url = '/move/' + $(this).attr('IMG');
	$.ajax({
	    url: url,
	    type: "POST",
	    success: function(data) { 
		$(td).closest('tr').hide()
	    },
	    error: function (data) {
		console.error(data.responseText);
	    }
	})
    })
  </script>

  </body>
  </html>
