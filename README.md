# SaCoFa
This repository is based on the paper "SaCoFa: Semantics-aware Control-flow Anonymization for Process Mining". It implements several instatiations of the SaCoFa approach for a trace-variant-query. Such a query generates a list of the control-flow behaviour present in an event log. For such queries the privacy is ensured by enforcing differential privacy. 

If you use our paper within an academic setting, please cite our paper:
```
@inproceedings{Fahrenkrog-Petersen21,
  author    = {Stephan A. Fahrenkrog{-}Petersen and
               Martin Kabierski and
               Fabian R{\"{o}}sel and
               Han van der Aa and
               Matthias Weidlich},
  editor    = {Claudio Di Ciccio and
               Chiara Di Francescomarino and
               Pnina Soffer},
  title     = {SaCoFa: Semantics-aware Control-flow Anonymization for Process Mining},
  booktitle = {3rd International Conference on Process Mining, {ICPM} 2021, Eindhoven,
               Netherlands, October 31 - Nov. 4, 2021},
  pages     = {72--79},
  publisher = {{IEEE}},
  year      = {2021},
  url       = {https://doi.org/10.1109/ICPM53251.2021.9576857},
  doi       = {10.1109/ICPM53251.2021.9576857},
  timestamp = {Fri, 29 Oct 2021 16:42:40 +0200},
  biburl    = {https://dblp.org/rec/conf/icpm/Fahrenkog-Petersen21.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```


## Requirements
To run our algorithm you need the following Python packages:
- NumPy (http://www.numpy.org)
- PM4Py (https://pm4py.fit.fraunhofer.de)
- OpyenXES (https://github.com/opyenxes/OpyenXes)

## How to run SaCoFa
If you want to run SaCoFa you should use the file "callprivatize.py". The different parameters of SaCoFa can be changed within the file. We additionally, provide the evaluation scripts used for our paper in the directory "Evaluation".

## License
This project is available under MIT license. However, libaries used by this project might come with different licenses. If you use this project in a academic setting, we ask you to cite our respective paper.



## How to contact us
SaCoFa was developed at the Database and Information Systems group of Humboldt-Universität zu Berlin. If you want to contact us, just send us a mail at: fahrenks || hu-berlin.de
