async function sendPrompt(){

    const prompt = document.getElementById("prompt").value

    const response = await fetch("/analyze",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            prompt: prompt
        })
    })

    const data = await response.json()

    document.getElementById("result").innerHTML = `
        <h2>AI Response</h2>
        <p>${data.answer}</p>

        <h2>Pollution Estimate</h2>
        <p>Tokens: ${data.pollution.tokens}</p>
        <p>Energy: ${data.pollution.energy} kWh</p>
        <p>CO2: ${data.pollution.co2} kg</p>
    `
}