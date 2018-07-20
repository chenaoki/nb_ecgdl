FROM chenaoki/docker_std:1.0.0

WORKDIR /mnt
RUN mkdir /mnt/ext

WORKDIR $NOTEBOOK_HOME
RUN git clone https://github.com/MIT-LCP/wfdb-python.git
WORKDIR $NOTEBOOK_HOME/wfdb-python
RUN pip install .

RUN pip install --upgrade pip

RUN pip install tensorflow
RUN pip install keras
    
RUN conda install -y scikit-learn

CMD ["sh", "-c", "jupyter notebook > $NOTEBOOK_HOME/log.txt 2>&1"]
