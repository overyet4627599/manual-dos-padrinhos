document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // DADOS DA MISSÃO
    // ==========================================

    const dados = {

        resposta: "",

        brincadeira: "",

        comida: "",

        sono: "",

        promessa: ""

    };


    // ==========================================
    // ELEMENTOS
    // ==========================================

    const screens =
        document.querySelectorAll(".screen");

    const steps =
        document.querySelectorAll(".step");

    const yesButton =
        document.getElementById("yesButton");

    const noButton =
        document.getElementById("noButton");

    const brincadeiraButton =
        document.getElementById("brincadeiraButton");

    const comidaButton =
        document.getElementById("comidaButton");

    const sonoButton =
        document.getElementById("sonoButton");

    const finishButton =
        document.getElementById("finishButton");

    const options =
        document.querySelectorAll(".option");


    // ==========================================
    // TROCAR TELA
    // ==========================================

    function mostrarTela(numero) {

        screens.forEach(function (screen) {

            screen.classList.remove("active");

        });


        const tela =
            document.getElementById(
                "screen" + numero
            );


        if (tela) {

            tela.classList.add("active");

        }


        steps.forEach(function (step) {

            const numeroStep =
                Number(
                    step.dataset.step
                );


            if (numeroStep <= numero) {

                step.classList.add("active");

            } else {

                step.classList.remove("active");

            }

        });


        window.scrollTo({

            top: 0,

            behavior: "smooth"

        });

    }


    // ==========================================
    // SIM
    // ==========================================

    yesButton.addEventListener(
        "click",
        function () {

            dados.resposta =
                "SIM! A VOVÓ ACEITOU A MISSÃO ❤️";

            mostrarTela(2);

        }
    );


    // ==========================================
    // NÃO FOGE
    // ==========================================

    function fugirDoNao() {

        const largura =
            window.innerWidth -
            noButton.offsetWidth -
            20;

        const altura =
            window.innerHeight -
            noButton.offsetHeight -
            20;


        const x =
            Math.max(
                10,
                Math.random() * largura
            );


        const y =
            Math.max(
                10,
                Math.random() * altura
            );


        noButton.style.position =
            "fixed";

        noButton.style.left =
            x + "px";

        noButton.style.top =
            y + "px";

        noButton.style.zIndex =
            "9999";

    }


    noButton.addEventListener(
        "mouseenter",
        fugirDoNao
    );


    noButton.addEventListener(
        "touchstart",
        function (event) {

            event.preventDefault();

            fugirDoNao();

        }
    );


    noButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            fugirDoNao();

        }
    );


    // ==========================================
    // SELEÇÃO DAS OPÇÕES
    // ==========================================

    options.forEach(function (option) {

        option.addEventListener(
            "click",
            function () {

                const categoria =
                    option.dataset.category;


                const valor =
                    option.dataset.value;


                options.forEach(
                    function (outraOpcao) {

                        if (
                            outraOpcao.dataset.category ===
                            categoria
                        ) {

                            outraOpcao.classList.remove(
                                "selected"
                            );

                        }

                    }
                );


                option.classList.add(
                    "selected"
                );


                dados[categoria] =
                    valor;

            }
        );

    });


    // ==========================================
    // BRINCADEIRA
    // ==========================================

    brincadeiraButton.addEventListener(
        "click",
        function () {

            if (!dados.brincadeira) {

                alert(
                    "Escolha uma brincadeira para a Lolô 👶❤️"
                );

                return;

            }


            mostrarTela(3);

        }
    );


    // ==========================================
    // COMIDA
    // ==========================================

    comidaButton.addEventListener(
        "click",
        function () {

            if (!dados.comida) {

                alert(
                    "Escolha a comidinha da Lolô 🍌❤️"
                );

                return;

            }


            mostrarTela(4);

        }
    );


    // ==========================================
    // SONO
    // ==========================================

    sonoButton.addEventListener(
        "click",
        function () {

            if (!dados.sono) {

                alert(
                    "Escolha como será a hora da soneca 😴❤️"
                );

                return;

            }


            mostrarTela(5);

        }
    );


    // ==========================================
    // FINALIZAR
    // ==========================================

    finishButton.addEventListener(
        "click",
        function () {

            if (!dados.promessa) {

                alert(
                    "Escolha uma promessa para a Lolô ❤️"
                );

                return;

            }


            // ==================================
            // MOSTRAR RESUMO
            // ==================================

            document.getElementById(
                "finalBrincadeira"
            ).textContent =
                dados.brincadeira;


            document.getElementById(
                "finalComida"
            ).textContent =
                dados.comida;


            document.getElementById(
                "finalSono"
            ).textContent =
                dados.sono;


            document.getElementById(
                "finalPromessa"
            ).textContent =
                dados.promessa;


            // ==================================
            // PREENCHER EMAIL
            // ==================================

            document.getElementById(
                "emailResposta"
            ).value =
                dados.resposta;


            document.getElementById(
                "emailBrincadeira"
            ).value =
                dados.brincadeira;


            document.getElementById(
                "emailComida"
            ).value =
                dados.comida;


            document.getElementById(
                "emailSono"
            ).value =
                dados.sono;


            document.getElementById(
                "emailPromessa"
            ).value =
                dados.promessa;


            // ==================================
            // ENVIAR EMAIL
            // ==================================

            document
                .getElementById("emailForm")
                .submit();


            // ==================================
            // MOSTRAR FINAL
            // ==================================

            screens.forEach(
                function (screen) {

                    screen.classList.remove(
                        "active"
                    );

                }
            );


            document
                .getElementById("finalScreen")
                .classList.add("active");


            document
                .getElementById("progress")
                .style.display =
                "none";


            criarCoracoes();

        }
    );


    // ==========================================
    // CORAÇÕES
    // ==========================================

    function criarCoracoes() {

        const container =
            document.querySelector(
                ".background-hearts"
            );


        for (
            let i = 0;
            i < 35;
            i++
        ) {

            const heart =
                document.createElement(
                    "div"
                );


            heart.className =
                "floating-heart";


            heart.textContent =
                Math.random() > 0.5
                    ? "❤️"
                    : "♡";


            heart.style.left =
                Math.random() * 100 +
                "%";


            heart.style.fontSize =
                12 +
                Math.random() * 22 +
                "px";


            heart.style.animationDuration =
                4 +
                Math.random() * 6 +
                "s";


            heart.style.animationDelay =
                Math.random() * 3 +
                "s";


            container.appendChild(
                heart
            );

        }

    }


    // ==========================================
    // CORAÇÕES CONTÍNUOS
    // ==========================================

    setInterval(
        function () {

            const container =
                document.querySelector(
                    ".background-hearts"
                );


            const heart =
                document.createElement(
                    "div"
                );


            heart.className =
                "floating-heart";


            heart.textContent =
                "♡";


            heart.style.left =
                Math.random() * 100 +
                "%";


            heart.style.fontSize =
                12 +
                Math.random() * 15 +
                "px";


            heart.style.animationDuration =
                6 +
                Math.random() * 4 +
                "s";


            container.appendChild(
                heart
            );


            setTimeout(
                function () {

                    heart.remove();

                },
                10000
            );

        },
        1200
    );

});