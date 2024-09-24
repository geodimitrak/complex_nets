% Authors: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos

%load BCT package
% addpath('C:\MATLAB\2019_03_03_BCT');

% the graph can be found at:
% PDC = EEG.CAT.Conn.PDC;

% freq = 10;
% G = mean(PDC(:,:,freq,:), 4); %mean accross time

%load graph
load('graph.mat');

%set sparsity level
sparsity = 0.2;
GS = threshold_proportional(G, sparsity);

%check if all nodes are connected in one component
c = graphconncomp(GS, 'weak',1); %if c==1, there is one connected component, else we need larger value of sparsity

%make it symmetric
A = (GS>0)|(GS'>0);
GS(A) = G(A);

%calculate Clustering Coefficient
CC = mean(clustering_coef_bu(GS));

%calculate Path Length
Lengths = weight_conversion(GS,'lengths');
% D: distances in 'steps'
D = distance_bin(Lengths);
%calculate characteristic path length, global efficiency 
[L,Eff_glob] = charpath(D, 0, 0); 

%calculate local efficiency
Eff_loc = mean(efficiency_bin(GS, 2));   

%calculate betweenness centrality
BC = mean(betweenness_bin(GS));
