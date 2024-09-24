% Authors: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos

%load BCT package
% addpath('C:\MATLAB\2019_03_03_BCT'); %change to appropriate folder

% Using EEGLAB and SIFT plugin , the graph can be found at:
% PDC = EEG.CAT.Conn.PDC;

%get graph at 7 Hz
%freq = 7;
%G = mean(PDC(:,:,freq,:), 4); %mean accross time (4th dimension)


%load graph
load('graph.mat');

%set sparsity level
sparsity = 0.2;
%use BCT function to apply sparsity level
GS = threshold_proportional(G, sparsity);

%check number of connected components
c = graphconncomp(GS, 'weak',1); %if c==1, there is one connected component, else we need larger value of sparsity


%make graph symmetric
A = (GS>0)|(GS'>0);
GS(A) = G(A);

%calculate clustering cofficient (CC)
CC_all = clustering_coef_bu(GS); %CC per node
CC = mean(CC); % average CC for graph

%get distancese between all nodes in "steps"
Lengths = weight_conversion(GS, 'lengths');
D = distance_bin(Lengths); 

%calculate characteristic path length (L) and global efficiency
[L, Eff_glob] = charpath(D, 0, 0); 

%calculate local efficiency
Eff_loc_all = efficiency_bin(GS, 2); %Local efficiency for all nodes
Eff_loc = mean(Eff_loc_all); %average local efficiency for graph

%calculate betweenness centrality
BC = mean(betweenness_bin(GS));

