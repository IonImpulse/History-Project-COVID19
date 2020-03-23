function returnResults() {
    var sex = document.forms["mainform"]["sex"].value;
    var age = document.forms["mainform"]["age"].value;
    if (isInt(age) == false) {
        alert("Please input a number for age");
        return false;
    } else {
        if (parseInt(age) > 105) {
            alert("Please input an age lower then 105");
            return false;
        } else {
            document.getElementById("results").innerHTML = getResults(sex, age);            
        }
    }
}
function isInt(value) {
    var x;
    if (isNaN(value)) {
      return false;
    }
    x = parseFloat(value);
    return (x | 0) === x;
}
function getResults(sex, age) {
    var data = loadFile(sex);
    var hosp_num = data[0][age]
    var mortal_num = data[1][age]

    hosp_num = Math.round(hosp_num * 100);
    mortal_num = Math.round(mortal_num * 100);

    return "Relative chance of hospitalization: " + toString(hosp_num) + "\nRelative change of death: " + toString(mortal_num);
}

function loadFile(sex) {
    var name = ""
    
    if (sex == "male") {    
        name = "data/regressed_male_calculator_data.csv"
    } else {
        name = "data/regressed_female_calculator_data.csv"
    }

    $.ajax({
        type: "GET",
        url: name,
        dataType: "text",
        success: function(data) {processData(data);}
        });

    // Let's process the data from the data file
    function processData(data) {
        var lines = data.split(/\r\n|\n/);

        //Set up the data arrays
        var hosp = [];
        var mortal = [];

        for (var j=0; j<lines.length; j++) {
        var values = lines[j].split(','); // Split up the comma seperated values
           hosp.push(parseFloat(values[0])); 
           mortal.push(parseFloat(values[1]));
        }

    // For display
    return [hosp, mortal]
    }
}