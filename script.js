
const form = document.getElementById('questions');
const responseTextarea = document.getElementById('response');
const question1 = document.getElementById('q1');
const question2 = document.getElementById('q2');
const question3 = document.getElementById('q3');
const question4 = document.getElementById('q4');
const question5 = document.getElementById('q5');
const question6 = document.getElementById('q6');

const submitButton = document.querySelector('button[type="submit"]');
const loadingIndicator = document.getElementById('loading'); // Define loadingIndicator


const API_KEY = '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';

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitButton.disabled = true;
    loadingIndicator.style.display = 'block';


    const q_1 = question1.value.trim();
    const q_2 = question2.value.trim();
    const q_3 = question3.value.trim();
    const q_4 = question4.value.trim();
    const q_5 = question5.value.trim();
    const q_6 = question6.value.trim();

    if (q_1) {
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEY}`,
                },
                body: JSON.stringify({
                    model: 'gpt-4',
                   /*  model: 'gpt-3.5-turbo', */
                   messages: [{ role: 'user', content: 'give me suggestions on what to plant considering that the average temperature range in my area during the growing season is '+ q_1 +', the rainfall our region gets is about '+ q_2 +' and the crops that we previously planted was '+ q_3 +' knowing that the crops that are currently in high demand in our local market is '+ q_4 +' The retention of moisture of my soil is '+ q_5 +' and the altitude of my farming location is '+ q_6 }],
                    //messages: [{ role: 'user', content: 'who was the first man in space' }],
                    
                    temperature: 1.0,
                    top_p: 0.7,
                    n: 1,
                    stream: false,
                    presence_penalty: 0,
                    frequency_penalty: 0,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                responseTextarea.value = data.choices[0].message.content;
            } else {
                responseTextarea.value = 'Error: Unable to process your request.';
            }
        } catch (error) {
            console.error(error);
            responseTextarea.value = 'Error: Unable to process your request.';
        }finally {
            // Re-enable the submit button after receiving the response
            submitButton.disabled = false;
            loadingIndicator.style.display = 'none';

        }
    }
});