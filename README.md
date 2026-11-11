# First implementation of segmentation

The goal of this first development is to use different colour masks and detect cataract fragments during surgery phase.

## Cataract fragment detection (ID tracking)

This is the first task of my thesis, to be able to track cataract fragments and follow them throughout the surgery. We will have bounding boxes for each fragment, persisten IDs (follow them all surgery phase)

For this script is important to do the correct dependencies installation, debugging of a single frame, full video processing and analysis of final CSV (useful for our protocol)

## Updates

### June 4th
For now, I've been implementing certain librariesw that already contain pre-trained models related to segmentation, but with the difference between version, it was not possible to continue. Searching for another tool. 

I'm looking for certain models and read their documentation on ho the training was done, before implementing my own ideas. Important to do a course for tis specifically

### June 9th
Today will be implementing a model called VideoMamba for video segmentation on more time consuming surgeries. Which follows ViT (vision transformers) standard architecture

VideoMamba refers to a class of neural architectures using structured state-space models for video sequence modeling and understanding

### June 10th
For my <cataract_fragments.py> code, I'll do a phase division of the code:

* Fragment segmentation -> masks
* Multiobject tracking -> IDs

By following the next pipeline:

Video MP4
    │
    ▼
Preprocess
    │
    ▼
Fragment segmentation
    │
    ▼
Bounding Boxes
    │
    ▼
Tracker per fragments
    │
    ▼
ID
    │
    ▼
Labeled video

As the first implementation without any pretrained model, just pure use of CV2.


**RESULTS:**
Pretty confusing results, the full focus is not on the eye but everywhere else. Some of the boxes and IDs tend to be in every other element but the iris, for example. Also, the light of the vide makes it confusing for the code to identify the parts we want to focus on. But this first approach is just using CV package and certain parameters. This next approach will be using a pre trained model. Maybe a cloned repository or model from hugging face. Could be YOLO model of Mamba Video. But it's important to customize it for medical videos.



### October

\section{Código base: pipeline de tracking sobre datos propios}
\label{sec:codigo-tracking}

Se desarrolló un notebook (\texttt{tracking\_catarata\_pipeline.ipynb}) con
el pipeline mínimo viable, validado de principio a fin sobre un video
sintético antes de correrlo sobre datos reales:

\begin{enumerate}
    \item Carga y recorte de video por fase quirúrgica.
    \item Selección manual de bounding box inicial + tracking con OpenCV
          (CSRT/KCF) — cumple el requisito de ``bounding boxes primero''.
    \item Extracción de centroide por frame y guardado como serie temporal.
    \item Cálculo de métricas: longitud de trayectoria, economía de
          movimiento, \emph{shaking}.
    \item Visualización: video con overlay de trayectoria + gráfica 2D
          coloreada por tiempo.
    \item Plantilla (no ejecutada, requiere GPU/pesos) para segmentación y
          tracking de fragmentos con SAM2.
    \item Plantilla de distancia a estructuras y log de eventos.
    \item Exportación de la plantilla de etiquetado en CSV.
\end{enumerate}

