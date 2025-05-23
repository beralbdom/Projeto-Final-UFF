%%
%% Customizações do abnTeX2 (http://abnTeX2.googlecode.com) para o Curso de Engenharia Civil da UFF
%%
%% This work may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either version 1.3
%% of this license or (at your option) any later version.
%% The latest version of this license is in
%%   http://www.latex-project.org/lppl.txt
%% and version 1.3 or later is part of all distributions of LaTeX
%% version 2005/12/01 or later.
%%
%% This work has the LPPL maintenance status `maintained'.
%% 
%% The Current Maintainer of this work is Jonas Alessi, alessi.jonas@gmail.com
%% 
%% Further information about abnTeX2 are available on http://abntex2.googlecode.com/
%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{abntex2-uff}[02/04/2023 Modelo da UFF baseado em abnTeX2]

%
% Repassa todos os parametros a classe abntex2, 
\DeclareOption*{%
  \PassOptionsToClass{\CurrentOption}{abntex2/abntex2}%
}
\ProcessOptions\relax
\LoadClass{abntex2/abntex2}
%---------------------------------------------------------------------------------

\newcommand{\supervisorname}{Supervisor:}
%-------
% informações do PDF
%-------
\makeatletter
\hypersetup{
    pdftitle={\@title}, 
    pdfauthor={\@author},
    pdfsubject={\imprimirpreambulo},
    pdfcreator={TexMaker},
    pdfkeywords={abnt}{latex}{abntex}{abntex2}{trabalho acadêmico}{uff}, 
    colorlinks=true,          % false: boxed links; true: colored links
    linkcolor=black,              % color of internal links
    urlcolor=black,              % color of internal links
    citecolor=black,            % color of links to bibliography
    bookmarksdepth=4
}
\makeatother
%-------
% Capa
%-------
\makeatletter
\renewcommand{\imprimircapa}{%
  \begin{capa}%
    \begin{center}
    % \vspace*{-1.2cm}
    {\imprimirinstituicao}
    
    \vspace*{4cm}
    
    {\imprimirautor}


    \vspace*{4cm}
    {\textbf{\imprimirtitulo}}

    \vspace*{2.5cm}
    {\imprimirtipotrabalho}

    \vspace*{\fill}
    
    {\imprimirlocal}
    \par
    {\imprimirdata}
    \end{center}
    % \vspace*{-0.7cm}
  \end{capa}
}

% Comandos de dados - supervisor
\providecommand{\imprimirsupervisorRotulo}{}
\providecommand{\imprimirsupervisor}{}
\newcommand{\supervisor}[2][\supervisorname]%
{\renewcommand{\imprimirsupervisorRotulo}{#1}%
\renewcommand{\imprimirsupervisor}{#2}}
%-----

% Cabecalho padrao
\makepagestyle{abntheadings}
\makeevenhead{abntheadings}{\ABNTEXfontereduzida\thepage}{}{\ABNTEXfontereduzida\textit\leftmark}
\makeoddhead{abntheadings}{
\ABNTEXfontereduzida%\textit \rightmark coloca o capitulo atual no header da pagina
}{}{\ABNTEXfontereduzida\thepage}
%\makeheadrule{abntheadings}{\textwidth}{\normalrulethickness} coloca o underline em baixo do header


%-----
%Folha de rosto
%-----
\renewcommand{\imprimirfolhaderosto}{
   \begin{center}

\vspace*{-1.2cm}
{\imprimirautor}

\vspace*{2.5cm}
{\textbf{\imprimirtitulo}}

\vspace*{2.5cm}
{\imprimirtipotrabalho}

\vspace*{2.5cm}

\abntex@ifnotempty{\imprimirpreambulo}{%
\hspace{.45\textwidth}
\begin{minipage}{.5\textwidth}
  \begin{SingleSpace}
     \imprimirpreambulo
  \end{SingleSpace}
\end{minipage}%
\vspace*{\fill}
}%

{ 

  \begin{SingleSpace}
   \imprimirorientadorRotulo~ \\ \imprimirorientador\par
   \abntex@ifnotempty{\imprimircoorientador}{
       { %\vspace*{-0.1cm}
         \imprimircoorientadorRotulo~ \\ \imprimircoorientador
       }
   }
  \abntex@ifnotempty{\imprimirsupervisor}{\par
      { %\vspace*{-0.1cm}
        \imprimirsupervisorRotulo~ \\ \imprimirsupervisor
       }
  }   
    \end{SingleSpace}
 }
\vspace*{\fill}

{\imprimirlocal}
\par
{\imprimirdata}
 \vspace*{-0.7cm}

\end{center}
\pagebreak
}


%------
%Folha de aprovacão
%------
\renewcommand{\ABNTEXsign}[1]{%
\parbox[t]{15cm}{\SingleSpacing\vspace*{\ABNTEXsignskip}%
\rule{15cm}{0.1pt}
\nopagebreak #1\par}
}


%---------
%Sumario
%regras da ABNT NBR 6027:2012
% \setlength\cftchapternumwidth{\cftparagraphnumwidth}
% \setlength\cftpartnumwidth{\cftparagraphnumwidth}
% \setlength\cftsubsectionnumwidth{\cftparagraphnumwidth}
% \setlength\cftsectionnumwidth{\cftparagraphnumwidth}
% \setlength\cftsubsubsectionnumwidth{\cftparagraphnumwidth}
% \setlength\cftsubsubsectionindent{8pt}
% \setlength\cftsubsectionindent{16pt}
% \setlength\cftsectionindent{24pt}
% \renewcommand*{\cftsubsectionfont}{\bfseries}

% REFERENCIA 
 \renewcommand{\bibsection}{%
   \chapter*{\bibname}
   \bibmark
   \ifnobibintoc\else
     \phantomsection
     \addcontentsline{toc}{chapter}{
     {\bibname}}
   \fi
   \prebibhook}

%Fonte (xx) e baselineskip (xx)
% \renewcommand{\ABNTEXchapterfontsize}{\fontsize{12}{12}\selectfont}
% \renewcommand{\ABNTEXsectionfontsize}{\fontsize{12}{12}\selectfont}
% \renewcommand{\ABNTEXsubsectionfontsize}{\fontsize{12}{12}\selectfont}
% \renewcommand{\ABNTEXsubsubsectionfontsize}{\fontsize{12}{12}\selectfont}

% ---
% Resumo e abstracts
\renewenvironment{resumo}[1][\resumoname]{%
% \PRIVATEbookmarkthis{#1}
% \renewcommand{\abstractnamefont}{\chaptitlefont}
% \renewcommand{\abstractname}{\ABNTEXchapterupperifneeded{#1}}
\pretextualchapter{#1}
\OnehalfSpacing
}{\PRIVATEclearpageifneeded}

\renewenvironment{resumoumacoluna}[1][\resumoname]{%
% \PRIVATEbookmarkthis{#1}
\renewcommand{\abstractnamefont}{\chaptitlefont}
\renewcommand{\abstractname}{\ABNTEXchapterupperifneeded{#1}}
\begin{onecolabstract}
\OnehalfSpacing
}{\end{onecolabstract}\PRIVATEclearpageifneeded}

%% remover a fonte sffamily
\renewcommand{\ABNTEXchapterfont}{\bfseries}

% tamanhos de fontes de section, subsection e subsubsection
% \setsecheadstyle{\ABNTEXsectionfontsize\ABNTEXsectionupperifneeded}
% \setsubsecheadstyle{\ABNTEXsubsectionfont\ABNTEXsubsectionfontsize\ABNTEXsubsectionupperifneeded\bfseries}
% \setsubsubsecheadstyle{\ABNTEXsubsubsectionfontsize}

%--Alinhar espaçamento caption
 \setlength{\belowcaptionskip}{0.2mm}
 \setlength{\abovecaptionskip}{0.5mm}
 %----
 
%Criar contorno
\newcommand{\borda}[1]{ 
\fboxrule=0.015pt  %largura da borda
  \framebox{
      #1
    }
}

%% Lista de quadros
\newcommand{\quadroname}{Quadro}
\newcommand{\listofquadrosname}{Lista de quadros}
\newfloat[chapter]{quadro}{loq}{\quadroname}
\newlistof{listofquadros}{loq}{\listofquadrosname}
\newlistentry{quadro}{loq}{0}
\counterwithout{quadro}{chapter}
\renewcommand{\cftquadroname}{\quadroname\space} 
\renewcommand*{\cftquadroaftersnum}{\hfill--\hfill}

% % Quadro na lista de ilustrações
\newcommand{\quadrofname}{Quadro}
\newfloat[chapter]{quadrof}{lof}{\quadrofname}
\newlistentry{quadrof}{lof}{0}
\counterwithout{quadrof}{chapter}
\renewcommand{\cftquadrofname}{\quadrofname\space} 
\renewcommand*{\cftquadrofaftersnum}{\hfill--\hfill}

% % Grafico
\newcommand{\graficoname}{Gr\'{a}fico}
\newfloat[chapter]{grafico}{lof}{\graficoname}
\newlistentry{grafico}{lof}{0}
\counterwithout{grafico}{chapter}
\renewcommand{\cftgraficoname}{\graficoname\space} 
\renewcommand*{\cftgraficoaftersnum}{\hfill--\hfill}

%% Fotografia
\newcommand{\fotografianame}{Fotografia}
\newfloat[chapter]{fotografia}{lof}{\fotografianame}
\newlistentry{fotografia}{lof}{0}
\counterwithout{fotografia}{chapter}
\renewcommand{\cftfotografianame}{\fotografianame\space} 
\renewcommand*{\cftfotografiaaftersnum}{\hfill--\hfill}

%% Fluxograma
\newcommand{\fluxogramaname}{Fluxograma}
\newfloat[chapter]{fluxograma}{lof}{\fluxogramaname}
\newlistentry{fluxograma}{lof}{0}
\counterwithout{fluxograma}{chapter}
\renewcommand{\cftfluxogramaname}{\fluxogramaname\space} 
\renewcommand*{\cftfluxogramaaftersnum}{\hfill--\hfill}

%% Organograma
\newcommand{\organogramaname}{Organograma}
\newfloat[chapter]{organograma}{lof}{\organogramaname}
\newlistentry{organograma}{lof}{0}
\counterwithout{organograma}{chapter}
\renewcommand{\cftorganogramaname}{\organogramaname\space} 
\renewcommand*{\cftorganogramaaftersnum}{\hfill--\hfill}

%% Diagrama
\newcommand{\diagramaname}{Diagrama}
\newfloat[chapter]{diagrama}{lof}{\diagramaname}
\newlistentry{diagrama}{lof}{0}
\counterwithout{diagrama}{chapter}
\renewcommand{\cftdiagramaname}{\diagramaname\space} 
\renewcommand*{\cftdiagramaaftersnum}{\hfill--\hfill}

%% Esquema
\newcommand{\esquemaname}{Esquema}
\newfloat[chapter]{esquema}{lof}{\esquemaname}
\newlistentry{esquema}{lof}{0}
\counterwithout{esquema}{chapter}
\renewcommand{\cftesquemaname}{\esquemaname\space} 
\renewcommand*{\cftesquemaaftersnum}{\hfill--\hfill}

%% Mapa
\newcommand{\mapaname}{Mapa}
\newfloat[chapter]{mapa}{lof}{\mapaname}
\newlistentry{mapa}{lof}{0}
\counterwithout{mapa}{chapter}
\renewcommand{\cftmapaname}{\mapaname\space} 
\renewcommand*{\cftmapaaftersnum}{\hfill--\hfill}

%% Desenho
\newcommand{\desenhoname}{Desenho}
\newfloat[chapter]{desenho}{lof}{\desenhoname}
\newlistentry{desenho}{lof}{0}
\counterwithout{desenho}{chapter}
\renewcommand{\cftdesenhoname}{\desenhoname\space} 
\renewcommand*{\cftdesenhoaftersnum}{\hfill--\hfill}

%Alinhar tabela a esquerda
\newcommand{\leftable}{
	\hskip-3.1cm
}

% ---
% Lista de abreviaturas e siglas
\renewenvironment{siglas}{%
\pretextualchapter{\listadesiglasname}
\OnehalfSpacing %Espaçamento 1.5
\begin{symbols}
}{%
\end{symbols}
\cleardoublepage
}

% ---
% Lista de sembolos
\renewenvironment{simbolos}{%
\pretextualchapter{\listadesimbolosname}
\OnehalfSpacing %Espaçamento 1.5
\begin{symbols}
}{%
\end{symbols}
\cleardoublepage
}
% ---

%Ajuste no espaçamento das listas de tabela, ilustrações e quadros
\setlength\cftbeforechapterskip{0pt}
\renewcommand{\insertchapterspace}{}

\makeatother
