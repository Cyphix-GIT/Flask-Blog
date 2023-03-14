$(document).ready(function () {
  $("#slug").keyup(function () {
    $.ajax({
      url: "",
      type: "get",
      contentType: "application/json",
      data: {
        user_input: $(this).val(),
      },
      success: function(response){
        if (response == "True") {
          $("#slug").css("border", "2px solid red");
          $("#slug").css("color", "red");
        } else {    
            $("#slug").css("border", "2px solid green");
            $("#slug").css("color", "green");
        }
      },
        error: function(error){
        console.log("Error")
        }
    });
  });
});
