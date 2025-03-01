const sendButton = () => {
    const sendButton = document.querySelector("button");
    const textInput = document.querySelector("inputField");

    if (textInput.value == null) {
        return 
    } else {
        getRequestAI()
    }

}


const getRequestAI = async (input) => {

    try {
        const response = await fetch("apiURL", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            console.log("Error fetching from api");
            return -1;
        }
        
        data = await response.json();
        
    } catch (error) {
        console.error(error);
    }
        
        
    }