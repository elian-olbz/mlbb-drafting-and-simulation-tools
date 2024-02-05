<a name="readme-top"></a>
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
    <a href="#about-the-project">About The Project</a>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#project-overview">Project Overview</a></li>
      <ul>
        <li><a href="#practice-draft">Practice Draft</a></li>
        <li><a href="#quick-draft">Quick Draft</a></li>
        <li><a href="#heatmap-viewer">Heatmap Viewer</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

This project is a drafting simulation and ananlysis tool for a popular MOBA game - Mobile Legends Bang Bang.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Built With

* Python
* PyQt6
* Tensorflow


<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Project Overview
### Main Page
![main_page](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/c8a736e6-a4f7-4956-a727-06b797aea65c)

## Practice Draft            

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Drafting is composed of an alternating banning and picking of heroes/characters in order to achieve the moset desirable line up or composition of heroes that will inrease the odds of winning the game.

You can select whether you want to simulate drafting on custom mode or versus AI Mode. The difference between Custom Mode and VS AI mode
is that you have the ability and freedom to undo the every move while in VS AI mode you can only reset everthing after finishing the drafting simulation. You will also have an AI opponent that is capable of drafting based on the the most picked heroes on MSC 2023 and MPL PH S12.

![practice_options](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/bbaa46a3-db5b-4ead-9f7b-b8a361a6bdcd)

VS AI mode choosing Blue side or Red side:

![side_options](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/ac05c7f4-b7b1-4a7b-b25e-7062d733d2fa)

Setting the Intelligence of the AI:

![intelligence](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/cc5d706f-d9dc-461f-9651-722938ac8937)

Darft Simulator Interface

![draft_sim1](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/3e2855b0-8a8d-4e97-b96d-5cf17b74b833)


![draft_full](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/9867dfd4-6586-4fa5-b5a1-eedcb5338c53)


![draft_reset](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/bea48be4-812a-41e9-80e4-30232683c353)



## Quick Draft

<p align="right">(<a href="#readme-top">back to top</a>)</p>


Quick Draft is the advanced version of the Practice Draft above. In quick draft there is no banning involved but it is focused more on data of the current hero composition that you have. These data is based on the results of previous Mobile Legends Bang Bang professional tournaments that were offiacilly hosted by Moonton. This include pick rate, ban rate, total winrate and others.

![quick_draft](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/45568fe4-73bb-4ca4-a167-bc13a542a9c4)


Quick Draft Interface

![quick_draft_main](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/03bd456a-7da8-4dfb-91a3-e09dfbf996b4)


Quick Draft Hero Selection Floating window/dialog:

![quick_hero_selection](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/46a009fc-1c77-4b1c-988d-ca215e65e919)


![quick_draft_full](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/6ef81bd8-5f70-4901-9a91-f1b0107c557e)

![quick_draft_reset](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/6649852c-e09d-4cca-a7ac-a98ecf22a385)


## Heatmap Viewer

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Heatmap viewer is a tool that uses the data fro a CSV file that was extracted from a video using a custom YOLOV8 model to reconstruct the video and add a colored dot on every location that forms a lines as the simulation continues. To learn more about the Tracking Model, you can click on this link:
[MLBB HERO TRACKING USING YOLOV8](https://github.com/elian-olbz/mlbb-hero-tracker-using-YOLOv8)


_Note: There is a conflict between the tensorflow version and other python packages that caused an error when this project is compiled to executable. The YoloV8 model was separated on another project which was originally included in this one._

![hmap_main](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/78522a91-e02b-4e61-bded-e619a66784bf)

Opening video file:

![hmap_file1](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/2d72aaa5-9b0f-4095-a379-01ffb187bf11)


Opening CSV file:

![hmap_file2](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/98f023ac-5962-4c4f-ac02-1728635e452b)

This is how it looks like after both files are opened. The left side is the video being played while on the right is using the data or the X and Y coordinates from the CSV and displaying the pictures of the heroes which approximately reconstructs and reflects the video.

![hmap_file3](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/97a307da-e14a-4423-8c0b-860fafea40fc)

After clicking "Start" button:

![hmap_start](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/32541242-c8b9-4ca3-9a2f-913a5654d1fe)

You can also hide some heroes on the right side using the radio buttons on the right:

![hmap_hide](https://github.com/elian-olbz/mlbb-drafting-and-simulation-tools/assets/88755620/b2424307-14fe-4902-813f-e0195745b366)

<p align="right">(<a href="#readme-top">back to top</a>)</p>




## Usage

_Note: This project uses the GPU version of tensorflow for the infernece of the neural network model as well as the trianing. Incomapatibility issues is expected for other devices._


