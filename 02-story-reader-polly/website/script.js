const UPLOAD_API =
"https://g1krkr8cnj.execute-api.ap-south-1.amazonaws.com/upload";

const STORIES_API =
"https://g1krkr8cnj.execute-api.ap-south-1.amazonaws.com/stories";


async function uploadStory(){

    let title=document.getElementById("title").value;

    let story=document.getElementById("story").value;

    if(title=="" || story==""){

        alert("Enter Title and Story");

        return;

    }

    await fetch(UPLOAD_API,{

        method:"POST",

        headers:{

            "Content-Type":"application/json"

        },

        body:JSON.stringify({

            title:title,

            story:story

        })

    });

    alert("Story Uploaded Successfully");

    document.getElementById("title").value="";
    document.getElementById("story").value="";

    loadStories();

}



async function loadStories(){

    let response=await fetch(STORIES_API);

    let data=await response.json();

    let html="";

    data.forEach(story=>{

        html+=`

        <div class="card">

        <h3>${story.story_name}</h3>

        <p><b>Voice:</b> ${story.voice}</p>

        <p><b>Uploaded:</b> ${story.upload_time}</p>

        <audio controls>

        <source src="${story.audio_url}" type="audio/mpeg">

        </audio>

        </div>

        `;

    });

    document.getElementById("stories").innerHTML=html;

}

loadStories();