const API_URL = "http://127.0.0.1:8000";


let sessionId = null;

let recognition = null;

let isListening = false;

let fullTranscript = "";

let alertAlreadyShown = false;



/* =========================================
   PAGE ELEMENTS
========================================= */


const startButton =
    document.getElementById("startProtection");


const stopButton =
    document.getElementById("stopProtection");


const transcriptBox =
    document.getElementById("liveTranscript");


const riskStatus =
    document.getElementById("riskStatus");


const confidenceBox =
    document.getElementById("confidence");


const redFlagsList =
    document.getElementById("redFlags");


const actionStepsList =
    document.getElementById("actionSteps");


const riskScore =
    document.getElementById("riskScore");


const categoryCount =
    document.getElementById("categoryCount");


const riskMeterFill =
    document.getElementById("riskMeterFill");


const analysisMessage =
    document.getElementById("analysisMessage");


const listeningIndicator =
    document.getElementById("listeningIndicator");



/* ALERT ELEMENTS */


const scamAlertOverlay =
    document.getElementById("scamAlertOverlay");


const alertTitle =
    document.getElementById("alertTitle");


const alertMessage =
    document.getElementById("alertMessage");


const alertReasons =
    document.getElementById("alertReasons");


closeAlert.addEventListener("click", function () {
    scamAlertOverlay.classList.remove("show");

    // Allow another alert if new threats are detected
    alertAlreadyShown = false;
});


const stopCallAlert =
    document.getElementById("stopCallAlert");



/* =========================================
   START BACKEND SESSION
========================================= */


async function startBackendSession() {


    const response =
        await fetch(

            `${API_URL}/session/start`,

            {

                method:
                    "POST"

            }

        );


    if (!response.ok) {

        throw new Error(

            "Could not start backend session."

        );

    }


    const data =
        await response.json();


    sessionId =
        data.session_id;


    console.log(

        "Session started:",

        sessionId

    );

}



/* =========================================
   SEND TRANSCRIPT
========================================= */


async function sendTranscript(text) {


    if (

        !sessionId ||

        !text.trim()

    ) {

        return;

    }


    try {


        const response =
            await fetch(

                `${API_URL}/session/${sessionId}/transcript`,

                {

                    method:
                        "POST",


                    headers: {

                        "Content-Type":
                            "application/json"

                    },


                    body:
                        JSON.stringify({

                            text:
                                text

                        })

                }

            );



        if (!response.ok) {


            const error =
                await response.text();


            console.error(

                "Backend error:",

                error

            );


            analysisMessage.innerText =

                "Backend analysis failed.";


            return;

        }



        const data =
            await response.json();



        console.log(

            "Backend response:",

            data

        );



        updateDashboard(data);


    }


    catch (error) {


        console.error(error);


        riskStatus.innerText =

            "Cannot connect to backend";

    }

}



/* =========================================
   SHOW SCAM ALERT
========================================= */


function showScamAlert(

    title,

    message,

    reasons = []

) {


    if (alertAlreadyShown) {

        return;

    }



    alertAlreadyShown =
        true;



    alertTitle.textContent =
        title;



    alertMessage.textContent =
        message;



    alertReasons.innerHTML =
        "";



    reasons

        .slice(0, 4)

        .forEach(reason => {


            const item =

                document.createElement(

                    "div"

                );



            item.className =

                "alert-reason";



            item.textContent =

                reason;



            alertReasons

                .appendChild(item);


        });



    scamAlertOverlay

        .classList

        .add("show");

}



/* =========================================
   ALERT BUTTONS
========================================= */


closeAlert.addEventListener(

    "click",

    function () {


        scamAlertOverlay

            .classList

            .remove("show");


    }

);



stopCallAlert.addEventListener(

    "click",

    function () {


        scamAlertOverlay

            .classList

            .remove("show");



        stopButton.click();


    }

);



/* =========================================
   UPDATE DASHBOARD
========================================= */


function updateDashboard(data) {


    const rules =

        data.rules_result || {};


    const verdict =

        data.verdict;



    const score =

        rules.total_score || 0;



    const categories =

        rules.categories_hit || 0;



    const matchedSignals =

        rules.matched_signals || [];



    /* =================================
       UPDATE SCORE
    ================================= */


    riskScore.innerText =

        score;



    categoryCount.innerText =

        `${categories} categories detected`;



    const meterPercentage =

        Math.min(

            (score / 20) * 100,

            100

        );



    riskMeterFill.style.width =

        `${meterPercentage}%`;



    /* =================================
       RULE-BASED RED FLAGS
    ================================= */


    redFlagsList.innerHTML =

        "";



    if (

        matchedSignals.length > 0

    ) {


        matchedSignals.forEach(

            signal => {


                const item =

                    document.createElement(

                        "li"

                    );



                const category =

                    (

                        signal.category ||

                        "suspicious signal"

                    )

                    .replaceAll(

                        "_",

                        " "

                    );



                item.textContent =

                    `"${signal.matched_text}" — ${category}`;



                redFlagsList

                    .appendChild(item);


            }

        );


    }


    else {


        redFlagsList.innerHTML =

            "<li>No suspicious signals detected yet.</li>";

    }



    /* =================================
       DEFAULT RECOMMENDATIONS
    ================================= */


    actionStepsList.innerHTML =

        "";



    if (score >= 6) {


        actionStepsList.innerHTML = `

            <li>
                Do not share OTP, UPI PIN,
                passwords or banking details.
            </li>

            <li>
                Do not transfer money requested
                during the call.
            </li>

            <li>
                Disconnect the suspicious call
                and independently verify the caller.
            </li>

            <li>
                If money has already been transferred,
                contact 1930 immediately.
            </li>

        `;


    }


    else if (score > 0) {


        actionStepsList.innerHTML = `

            <li>
                Stay cautious and do not share
                sensitive information.
            </li>

            <li>
                Verify the caller independently.
            </li>

            <li>
                Continue monitoring the conversation.
            </li>

        `;


    }


    else {


        actionStepsList.innerHTML =

            "<li>Continue monitoring the conversation.</li>";

    }



    /* =================================
       RULE-BASED ALERT
    ================================= */


    if (

        score >= 8

    ) {


        const reasons =

            matchedSignals.map(

                signal =>

                    `Detected "${signal.matched_text}"`

            );



        showScamAlert(

            "High-Risk Scam Pattern Detected",

            "Multiple dangerous scam indicators were detected in this conversation.",

            reasons

        );

    }



    /* =================================
       NO AI VERDICT YET
    ================================= */


    if (!verdict) {


        if (score === 0) {


            riskStatus.innerText =

                "No suspicious activity detected";



            confidenceBox.innerText =

                "Continuing to monitor the conversation.";



            analysisMessage.innerText =

                "No scam indicators detected yet.";


        }


        else {


            riskStatus.innerText =

                "⚠️ Suspicious signals detected";



            confidenceBox.innerText =

                "Waiting for AI analysis...";



            analysisMessage.innerText =

                `${score} risk points detected across ${categories} categories.`;


        }



        if (data.llm_error) {


            console.error(

                "Claude error:",

                data.llm_error

            );



            confidenceBox.innerText =

                "Rules-based protection active. AI analysis unavailable.";

        }



        return;

    }



    /* =================================
       AI VERDICT
    ================================= */


    const verdictType =

        verdict.verdict;



    if (

        verdictType === "scam"

    ) {


        riskStatus.innerText =

            "🚨 SCAM DETECTED";



        showScamAlert(

            "Scam Detected",

            verdict.explanation ||

            "AI analysis identified this conversation as a scam.",

            verdict.red_flags || []

        );


    }


    else if (

        verdictType === "likely_scam"

    ) {


        riskStatus.innerText =

            "⚠️ HIGH SCAM RISK";


    }


    else if (

        verdictType === "suspicious"

    ) {


        riskStatus.innerText =

            "⚠️ SUSPICIOUS ACTIVITY";


    }


    else {


        riskStatus.innerText =

            "✓ No major scam indicators";


    }



    /* =================================
       AI CONFIDENCE
    ================================= */


    confidenceBox.innerText =

        `AI Confidence: ${verdict.confidence}%`;



    /* =================================
       AI EXPLANATION
    ================================= */


    analysisMessage.innerText =

        verdict.explanation ||

        "Analysis complete.";



    /* =================================
       AI RED FLAGS
    ================================= */


    if (

        verdict.red_flags &&

        verdict.red_flags.length > 0

    ) {


        redFlagsList.innerHTML =

            "";



        verdict.red_flags.forEach(

            flag => {


                const item =

                    document.createElement(

                        "li"

                    );



                item.textContent =

                    flag;



                redFlagsList

                    .appendChild(item);


            }

        );

    }



    /* =================================
       AI ACTION STEPS
    ================================= */


    if (

        verdict.action_steps &&

        verdict.action_steps.length > 0

    ) {


        actionStepsList.innerHTML =

            "";



        verdict.action_steps.forEach(

            step => {


                const item =

                    document.createElement(

                        "li"

                    );



                item.textContent =

                    step;



                actionStepsList

                    .appendChild(item);


            }

        );

    }

}



/* =========================================
   SPEECH RECOGNITION
========================================= */


function setupSpeechRecognition() {


    const SpeechRecognition =

        window.SpeechRecognition ||

        window.webkitSpeechRecognition;



    if (!SpeechRecognition) {


        alert(

            "Speech recognition is not supported. Please use Google Chrome."

        );


        return false;

    }



    recognition =

        new SpeechRecognition();



    recognition.continuous =

        true;



    recognition.interimResults =

        true;



    recognition.lang =

        "en-IN";



    recognition.onresult =

        function (event) {


            let interimText =

                "";



            let finalText =

                "";



            for (

                let i =

                    event.resultIndex;


                i <

                    event.results.length;


                i++

            ) {


                const text =

                    event.results[i][0]

                        .transcript;



                if (

                    event.results[i]

                        .isFinal

                ) {


                    finalText +=

                        text;


                }


                else {


                    interimText +=

                        text;


                }

            }



            if (interimText) {


                transcriptBox.innerHTML =

                    `${fullTranscript}

                    <span style="opacity:0.5">

                        ${interimText}

                    </span>`;

            }



            if (

                finalText.trim()

            ) {


                fullTranscript +=

                    " " +

                    finalText.trim();



                transcriptBox.textContent =

                    fullTranscript.trim();



                transcriptBox.scrollTop =

                    transcriptBox.scrollHeight;



                sendTranscript(

                    finalText.trim()

                );

            }

        };



    recognition.onerror =

        function (event) {


            console.error(

                "Speech recognition error:",

                event.error

            );



            if (

                event.error ===

                "not-allowed"

            ) {


                riskStatus.innerText =

                    "Microphone permission denied";

            }

        };



    recognition.onend =

        function () {


            if (isListening) {


                try {


                    recognition.start();


                }


                catch (error) {


                    console.log(

                        "Restarting speech recognition..."

                    );

                }

            }

        };



    return true;

}



/* =========================================
   START PROTECTION
========================================= */


startButton.addEventListener(

    "click",

    async function () {


        try {


            startButton.disabled =

                true;



            riskStatus.innerText =

                "Starting protection...";



            await startBackendSession();



            const supported =

                setupSpeechRecognition();



            if (!supported) {


                startButton.disabled =

                    false;


                return;

            }



            /* RESET SESSION */


            fullTranscript =

                "";



            alertAlreadyShown =

                false;



            scamAlertOverlay

                .classList

                .remove("show");



            transcriptBox.innerText =

                "Listening...";



            riskScore.innerText =

                "0";



            categoryCount.innerText =

                "0 categories detected";



            riskMeterFill.style.width =

                "0%";



            redFlagsList.innerHTML =

                "<li>No suspicious signals detected yet.</li>";



            actionStepsList.innerHTML =

                "<li>Continue monitoring the conversation.</li>";



            /* START LISTENING */


            isListening =

                true;



            recognition.start();



            stopButton.disabled =

                false;



            listeningIndicator.innerText =

                "● Listening";



            listeningIndicator

                .classList

                .add("active");



            riskStatus.innerText =

                "🛡️ Protection Active";



            confidenceBox.innerText =

                "Listening for suspicious activity...";


        }


        catch (error) {


            console.error(error);



            riskStatus.innerText =

                "Could not connect to backend";



            startButton.disabled =

                false;

        }

    }

);



/* =========================================
   STOP PROTECTION
========================================= */


stopButton.addEventListener(

    "click",

    function () {


        isListening =

            false;



        if (recognition) {


            recognition.stop();

        }



        startButton.disabled =

            false;



        stopButton.disabled =

            true;



        listeningIndicator.innerText =

            "● Offline";



        listeningIndicator

            .classList

            .remove("active");



        riskStatus.innerText =

            "Protection stopped";



        confidenceBox.innerText =

            "The call is no longer being monitored.";

    }

);