$("#add").click(function(){
    var clone = $("#nfa-transitions .production-row").last().clone(true);
    clone.val("");
    clone.find("input").each(function() {
        $(this).val("");
    });
    clone.appendTo($("#production-rows"));
  
  });
  